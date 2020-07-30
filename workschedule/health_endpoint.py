from os import environ
import locust
from locust import between
from locust.user import HttpUser, TaskSet, task, User
from locust import event
import exit_handler
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

        assert response.elapsed < datetime.timedelta(seconds = 3), "health endpoint request took more than 3 second"

class WebsiteUser(HttpUser):
    host = get_host()

    tasks = [HealthEndpoint]
    wait_time = between(1, .5)

