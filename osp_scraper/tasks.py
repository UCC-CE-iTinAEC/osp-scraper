import logging

from rq.decorators import job
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer

from .services import redis_conn


logger = logging.getLogger(__name__)


def crawl(spider, *args, **kwargs):
    """Run a spider.

    Args:
        spider (str): The Scrapy `name` of the spider.
    """
    settings = get_project_settings()
    if kwargs.get('ignore_robots_txt') is True:
        settings.attributes.get('ROBOTSTXT_OBEY').value = False

    proc = CrawlerProcess(settings)
    try:
        proc.crawl(spider, *args, **kwargs)
        proc.start()
    except KeyError as err:
        # Log a warning if the scraper name is invalid instead of
        # causing the job to fail.
        logger.warning(err.args[0])


def get_crawl_job(timeout='24h'):
    """Returns a function that will add a crawl call to the Redis queue

    Args:
        timeout (int/string): the maximum runtime of the job
    """
    return job('default', connection=redis_conn, timeout=timeout)(crawl).delay


class LocalQueue():
    queue = []

    @classmethod
    def enqueue(cls, spider, *args, **kwargs):
        cls.queue.append((spider, args, kwargs))

    @classmethod
    def run(cls):
        runner = CrawlerRunner(get_project_settings())

        @defer.inlineCallbacks
        def deferred_crawl():
            for spider, args, kwargs in cls.queue:
                try:
                    yield runner.crawl(spider, *args, **kwargs)
                except KeyError as err:
                    # Log a warning if the scraper name is invalid instead of
                    # causing the job to fail.
                    logger.warning(err.args[0])
            reactor.stop()

        deferred_crawl()
        reactor.run()
