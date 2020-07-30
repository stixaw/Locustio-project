from os import environ
import locust
from locust.env import Environment
from locust.user import HttpUser, User, task
from locust import between, SequentialTaskSet 
import exit_handler
import testdata
import json
from random import randint
import datetime

def get_environment():
    if environ.get("TEST_CLIENT_ID"):
        client_id = environ.get("TEST_CLIENT_ID")
        client_secret = environ.get("TEST_CLIENT_SECRET")
        return client_id, client_secret

def get_host():
  if environ.get("TEST_API_URL"):
    host = environ.get("TEST_API_URL")
    return host


class BulkCreateSequence(SequentialTaskSet):

    def on_start(self):
        self.get_token()

    def get_token(self):
        get_env = get_environment()
        client_id = get_env[0]
        client_secret = get_env[1]

        print("Get Token")
        response = self.client.post("/auth/token", json={
            "client_id": client_id,
            "client_secret": client_secret
        }
        )
        if (response.status_code == 200):
            body = response.json()
            token = body['access_token']
            self.jwt = f'Bearer {token}'
            return self.jwt
        else:
            print(f'Status Code: {response.status_code}')
            self.interrupt()


    @task
    # put this onto the user instance for the taskset. (talk to Mark)
    def get_assignmentId(self):
      self.assignment_id = testdata.get_assignment_id()
      return self.assignment_id

    @task
    def create_worksite(self):
        default_worksites = testdata.get_default_worksites()
        url = "/assignments/%s/worksites/batchUpdateLabels" % self.assignment_id

        print("Create 3 Worksites")
        response = self.client.post(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        }, json=default_worksites
        )
        body = json.loads(response.text)
        if len(body['assignmentWorksites']) > 0:
            self.worksite_id = body['assignmentWorksites'][0]['worksiteId']
        assert response.elapsed < datetime.timedelta(seconds = 3), "createWorksite request took more than 3 second"
        return self.worksite_id  

    @task
    def bulk_create_shift(self):
        self.delete_shifts = []
        start_date = "2020-08-02"
        url = "/assignments/%s/shifts/bulk" % self.assignment_id

        random_shift_num = randint(5, 90)
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

        shifts = body['shifts']
        for s in shifts:
            self.delete_shifts.append(s['id'])
        assert response.elapsed < datetime.timedelta(seconds = 3), "Bulk Create Shifts for {0} shifts request took more than 3 second".format(random_shift_num)

    @task
    def get_shifts(self):

        url = "/assignments/%s/shifts" % self.assignment_id

        print("Get Shift")
        response = self.client.get(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        })
        assert response.elapsed < datetime.timedelta(seconds = 3), "Get Shifts request took more than 3 second"

    @task
    def query_endpoint(self):
        url = "/shifts/query?count=100&page=1&includeDeleted=true"

        print("Query select all shifts by assignmentId")
        response = self.client.post(url, headers={
              "Authorization": self.jwt,
              "Content-Type": "application/json"
          }, json={
              "where": {
                  "assignmentId": self.assignment_id
              }
          })
        assert response.elapsed < datetime.timedelta(seconds = 3), "Query get shifts by assignmentId request took more than 3 second"


class WebsiteUser(HttpUser):
    host = get_host()

    tasks = [BulkCreateSequence]
    wait_time = between(1, 1)
