from rq import Worker


class ScraperWorker(Worker):

    def request_stop(self, *args, **kwargs):
        """When SIGINT is sent to the worker (eg, if the Supervisor process
        group is restarted), immediately fail the running job and stop the
        worker. This avoids a scenario in which the worker gets shut down but
        not unregistered in Redis, causing it to get "marooned" in the admin.
        """
        job = self.get_current_job()

        if job:
            self.handle_job_failure(job)
            self.failed_queue.quarantine(job, 'Worker shutdown.')

        self.request_force_stop(*args, **kwargs)
