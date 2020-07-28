from locust import HttpUser, TaskSet, task, between, SequentialTaskSet, User
import uuid
import env
import json
from os import environ


def get_environment():
    if environ.get("DOCKER_ENV"):
        return environ.get("DOCKER_ENV")
    else:
        print("no env")
        return "dev"


class GetToken(TaskSet):

    @task
    def get_token(self):
        run_env = get_environment()
        print("ENV: {0}".format(run_env))

        results = env.get_tokensecrets(run_env)
        client_id = results[1]
        client_secret = results[2]

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
    run_env = get_environment()
    response = env.get_tokensecrets(run_env)
    host = response[0]

    tasks = [GetToken]
    wait_time = between(1, 1)
