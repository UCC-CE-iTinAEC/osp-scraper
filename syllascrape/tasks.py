from __future__ import absolute_import

from .celery import app
from .spiders import Spider

from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from billiard import Process
from scrapy.utils.project import get_project_settings

class CrawlerSubprocess(Process):
    """Crawling via subprocess under celery

    Based on http://stackoverflow.com/a/22202877 and
    http://doc.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.runner = CrawlerRunner(get_project_settings())
        self.args = args
        self.kwargs = kwargs

    def run(self):
        d = self.runner.crawl(Spider, *self.args, **self.kwargs)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()


@app.task
def crawl(*args, **kwargs):
    proc = CrawlerSubprocess(*args, **kwargs)
    proc.start()
    proc.join()
