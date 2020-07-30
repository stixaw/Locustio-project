from os import environ
from locust import HttpUser, TaskSet, task, between, SequentialTaskSet, User
import uuid
import env
import json
import datetime


def get_host():
  if environ.get("TEST_API_URL"):
    host = environ.get("TEST_API_URL")
    return host

class HealthEndpoint(TaskSet):

    @task
    def health_endpoint(self):
      url = "/health"

      response = self.client.get(url)

      if (response.status_code == 200):
        assert response.elapsed < datetime.timedelta(seconds = 3), "health endpoint request took more than 3 second"

class WebsiteUser(HttpUser):
    host = get_host()

    tasks = [HealthEndpoint]
    wait_time = between(1, .5)

