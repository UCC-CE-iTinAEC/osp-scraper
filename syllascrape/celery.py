from __future__ import absolute_import

from celery import Celery

app = Celery('syllascrape',
             broker='redis://localhost:6379/0',
             include=['syllascrape.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERYD_MAX_TASKS_PER_CHILD=1,
)

if __name__ == '__main__':
    app.start()
