from binder.celery import Celery

from .views import save_values_to_db


app = Celery()

@app.task
def save_to_db():
    save_values_to_db()
