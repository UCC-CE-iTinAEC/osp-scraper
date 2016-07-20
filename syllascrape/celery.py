from __future__ import absolute_import

from celery import Celery

app = Celery('syllascrape',
             include=['syllascrape.tasks'])

app.config_from_object('celeryconfig')
app.conf.update(
    CELERYD_MAX_TASKS_PER_CHILD=1, # start a new celery process for each task
)

if __name__ == '__main__':
    app.start()
