from os import environ
from locust import HttpUser, TaskSet, task, between, SequentialTaskSet, User
import uuid
import env
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


class UserBehavior(SequentialTaskSet):

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
      self.assignment_id = env.get_assignment_id()
      return self.assignment_id

    @task
    def create_worksite(self):
        default_worksites = env.get_default_worksites()
        url = "/assignments/%s/worksites/batchUpdateLabels" % self.assignment_id

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
    def get_worksites(self):
        url = "/assignments/%s/worksites" % self.assignment_id

        response = self.client.get(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        })
        assert response.elapsed < datetime.timedelta(seconds = 3), "Get Worksites request took more than 3 seconds"


    @task
    def create_shift(self):
        start_date = "2020-07-30"
        url = "/assignments/%s/shifts" % self.assignment_id

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
        assert response.elapsed < datetime.timedelta(seconds = 3), "createWorksite request took more than 3 seconds"

    @task
    def get_shifts(self):
        url = "/assignments/%s/shifts" % self.assignment_id

        response = self.client.get(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        })
        body = json.loads(response.text)
        shifts = body['shifts']
        self.shift_id = shifts[0]['id']

        assert response.elapsed < datetime.timedelta(seconds = 3), "Get Shifts request took more than 3 seconds"
        return self.shift_id

    @task
    def update_shift(self):
        start_date = "2020-08-01"
        end_date = "2020-08-01"
        url = "/assignments/%s/shifts/%s" % (self.assignment_id, self.shift_id)

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
        assert response.elapsed < datetime.timedelta(seconds = 3), "Update shift request took more than 3 seconds"

    @task
    def delete_shift(self):
        url = "/assignments/%s/shifts/%s" % (self.assignment_id, self.shift_id)

        response = self.client.delete(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        })
        assert response.elapsed < datetime.timedelta(seconds = 3), "Delete shift request took more than 3 seconds"

    @task
    def bulk_create_shift(self):
        self.delete_shifts = []
        start_date = "2020-08-02"
        url = "/assignments/%s/shifts/bulk" % self.assignment_id

        shifts_array = []
        for i in range(25):
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

        assert response.elapsed < datetime.timedelta(seconds = 3), "Bulk Create 25 shifts took more than 3 seconds"
        return self.delete_shifts

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

    @task
    def bulk_delete_shifts(self):

        url = "/assignments/%s/shifts" % (self.assignment_id)
        response = self.client.delete(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        }, json={
            "ids": self.delete_shifts
        })
        assert response.elapsed < datetime.timedelta(seconds = 3), "Bulk Delete 25 shifts took more than 3 seconds"

class WebsiteUser(HttpUser):
    host = get_host()

    tasks = [UserBehavior]
    wait_time = between(1, 2)

