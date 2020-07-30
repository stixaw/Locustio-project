from os import environ
import locust
from locust.env import Environment
from locust.user import HttpUser, User, TaskSet, task
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

class QueryEndpoint(TaskSet):


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
            print(self.jwt)
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
    def shifts_by_assignment_id(self):
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
        body = json.loads(response.text)
        print("query results {0}".format(body))
        assert response.elapsed < datetime.timedelta(seconds = 3), "Query get shifts by assignmentId request took more than 3 second"

    @task
    def shifts_by_assignment_id_since(self):
      url = "/shifts/query?count=100&page=1"

      print("Query select shifts by assignment id since date")
      response = self.client.post(url, headers={
            "Authorization": self.jwt,
            "Content-Type": "application/json"
        }, json={
            "where": {
              "startDate": {
                "$gte": "2020-03-13T06:00:00.000Z"
              },
              "assignmentId": self.assignment_id
            }
        })
      body = json.loads(response.text)
      print("query results {0}".format(body))
      assert response.elapsed < datetime.timedelta(seconds = 3), "Query get shifts by assignmentId request took more than 3 second"
