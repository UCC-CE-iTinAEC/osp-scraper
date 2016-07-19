# URL of redis
BROKER_URL = 'redis://localhost:6379/0'

# start a new celery process for each task
CELERYD_MAX_TASKS_PER_CHILD=1