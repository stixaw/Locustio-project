from locust import HttpUser, TaskSet, task, between, SequentialTaskSet, User
import json
from os import environ

def get_environment():
    if environ.get("TEST_CLIENT_ID"):
        client_id = environ.get("TEST_CLIENT_ID")
        client_secret = environ.get("TEST_CLIENT_SECRET")
        return client_id, client_secret

def get_host():
  if environ.get("TEST_API_URL"):
    host = environ.get("TEST_API_URL")
    return host


class GetToken(TaskSet):

    @task
    def get_token(self):
        get_env = get_environment()
        client_id = get_env[0]
        client_secret = get_env[1]

        response = self.client.post("/auth/token", json={
            "client_id": client_id,
            "client_secret": client_secret
        }
        )

        if (response.status_code == 200):
            body = response.json()
            token = body['access_token']
            self.jwt = f'Bearer {token}'
            print(self.jwt)
            return self.jwt
        else:
            print(f'Status Code: {response.status_code}')
            self.interrupt()


class WebsiteUser(HttpUser):
    host = get_host()

    tasks = [GetToken]
    wait_time = between(1, 1)
