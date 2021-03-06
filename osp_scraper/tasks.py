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

    proc = CrawlerProcess(settings)
    try:
        proc.crawl(spider, *args, **kwargs)
        proc.start()
    except KeyError as err:
        # Log a warning if the scraper name is invalid instead of
        # causing the job to fail.
        # NOTE: If there is any other type of error, the job will fail, and all
        # the jobs that depend on it will fail as well.
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
                    # NOTE: If there is any other type of error, the job will
                    # fail, and all the jobs that depend on it will fail as
                    # well.
                    logger.warning(err.args[0])

            # XXX: If all the names fail, then trying to run
            # `reactor.stop()` will give an "Unhandled error in
            # Deferred" complaint and hang.  It will also hang in
            # general if no spiders have been run.  I assume there's
            # some twisted-way to handle this, but for now, just log an
            # error.
            if reactor.running:
                reactor.stop()
            else:
                logger.critical("LocalQueue: No valid scraper names found.")

        deferred_crawl()
        reactor.run()
