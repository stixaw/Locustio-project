from os import environ
from locust import HttpUser, TaskSet, task, between, SequentialTaskSet, User
import uuid
import env
import json

def get_environment():
    if environ.get("DOCKER_ENV"):
        return environ.get("DOCKER_ENV")
    else:
        print("no env")
        return "dev"


class UpdateShift(SequentialTaskSet):

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
        message = "Create worksites response: !!AssignmentId= {1}: @@Worksites= {0}".format(
            body['assignmentWorksites'], self.assignment_id)

        print(message)

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
    def create_shift(self):
        start_date = "2020-07-30"
        url = "/assignments/%s/shifts" % self.assignment_id

        print("Create a Shift")
        response = self.client.post(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        }, json={

            "startDate": start_date,
            "status": "Confirmed",
            "worksites": [{
                "worksiteId": self.worksite_id
            }]

        })
        body = json.loads(response.text)
        message = "Create Shift response: = {0}".format(body)

        print(message)

    @task
    def get_shifts(self):
        url = "/assignments/%s/shifts" % self.assignment_id

        print("Get Shifts")
        response = self.client.get(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        })

        body = json.loads(response.text)
        shifts = body['shifts']
        self.shift_id = shifts[0]['id']
        message = "Shifts count = {0}".format(len(body['shifts']))
        print(message)
        return self.shift_id


    @task
    def update_shift(self):
        start_date = "2020-08-02"
        end_date = "2020-08-02"
        url = "/assignments/%s/shifts/%s" % (self.assignment_id, self.shift_id)

        print("Update Shift")
        response = self.client.put(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        }, json={
            "endDate": start_date,
            "startDate": end_date,
            "status": "Confirmed",
            "worksites": [{
                "worksiteId": self.worksite_id
            }]
        })
        body = json.loads(response.text)
        message = "Update Shift response: {0} with shift id: {1}".format(body, self.shift_id)

        print(message)


class WebsiteUser(HttpUser):
    run_env = get_environment()
    response = env.get_tokensecrets(run_env)
    host = response[0]

    tasks = [UpdateShift]
    wait_time = between(1, 1)
