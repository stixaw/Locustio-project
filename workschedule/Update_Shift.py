from os import environ
import locust
from locust.env import Environment
from locust.user import HttpUser, User, task
from locust import between, SequentialTaskSet 
import exit_handler
import testdata
import json
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


class UpdateShift(SequentialTaskSet):

    def on_start(self):
        self.get_token()

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
            return self.jwt
        else:
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
        assert response.elapsed < datetime.timedelta(seconds = 3), "Create Shift request took more than 3 second"

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
        assert response.elapsed < datetime.timedelta(seconds = 3), "Get Shifts request took more than 3 second"
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

    tasks = [UpdateShift]
    wait_time = between(1, 1)
