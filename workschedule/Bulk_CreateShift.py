from os import environ
from locust import HttpUser, TaskSet, task, between, SequentialTaskSet, User
import uuid
import env
import json
from random import randint

def get_environment():
    if environ.get("DOCKER_ENV"):
        return environ.get("DOCKER_ENV")
    else:
        print("no env")
        return "dev"


class BulkCreateSequence(SequentialTaskSet):

    def on_start(self):
        self.get_token()

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

    @task
    # put this onto the user instance for the taskset. (talk to Mark)
    def get_assignmentId(self):
      self.assignment_id = env.get_assignment_id()
      return self.assignment_id

    @task
    def create_worksite(self):
        default_worksites = env.get_default_worksites()
        url = "/assignments/%s/worksites/batchUpdateLabels" % self.assignment_id

        print("Create 3 Worksites")
        response = self.client.post(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        }, json=default_worksites
        )

        body = json.loads(response.text)
        message = "!!AssignmentId= {1}: @@Worksites= {0}".format(
            body['assignmentWorksites'], self.assignment_id)

        print("Create worksites response: {0}".format(message))

    @task
    def get_worksites(self):
        url = "/assignments/%s/worksites" % self.assignment_id

        print("Get Worksites")
        response = self.client.get(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        })
        body = json.loads(response.text)
        if len(body['assignmentWorksites']) > 0:
            self.worksite_id = body['assignmentWorksites'][0]['worksiteId']

        message = "AssignmentId = {1} Worksite Id = {0}".format(
            body['assignmentWorksites'][0]['worksiteId'], self.assignment_id)

        print(message)
        return self.worksite_id

    @task
    def bulk_create_shift(self):
        self.delete_shifts = []

        start_date = "2020-08-02"
        url = "/assignments/%s/shifts/bulk" % self.assignment_id

        random_shift_num = randint(5, 100)
        print("bulk shifts to create: {0}".format(random_shift_num))
        shifts_array = []

        for i in range(random_shift_num):
            shifts_array.append({
                      "startDate": start_date,
                      "status": "Confirmed",
                      "worksites": [{
                          "worksiteId": self.worksite_id
                      }]
                  },)

        response = self.client.post(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        }, json={
              "shifts": shifts_array
        })
        body = json.loads(response.text)
        message = "Shifts count = {0}".format(len(body['shifts']))
        print(message)

        shifts = body['shifts']
        for s in shifts:
            self.delete_shifts.append(s['id'])
        print("Shifts count in delete shifts array = {0}".format(len(self.delete_shifts)))

    @task
    def get_shifts(self):
        url = "/assignments/%s/shifts" % self.assignment_id

        print("Get Shifts")
        response = self.client.get(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        })

        body = json.loads(response.text)
        message = "Get Shifts count = {0}".format(len(body['shifts']))

        print(message)


class WebsiteUser(HttpUser):
    run_env = get_environment()
    response = env.get_tokensecrets(run_env)
    host = response[0]

    tasks = [BulkCreateSequence]
    wait_time = between(1, 1)
