

from rq import Worker


class ScraperWorker(Worker):

    def request_stop(self, *args, **kwargs):
        self.request_force_stop(*args, **kwargs)
