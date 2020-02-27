from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task
import uuid
import env
import json

#ugly globals
assignment_id = ""
delete_shifts = []
shift_id = ""
target = ""
worksite_id = ""

class GetShifts(TaskSequence):

  def on_start(self):
    self.getToken()

  def getToken(self):

    results = env.get_tokensecrets("stage")
    client_id = results[1]
    client_secret = results[2]
   
    print("Get Token")
    response = self.client.post("/auth/token", json=
    {
      "client_id": client_id,
      "client_secret": client_secret
    }
    )
    json_res = response.json()
    self.token = json_res['access_token']
    self.jwt = "Bearer {0}".format(self.token)

  @seq_task(1)
  def create_worksite(self):
    global assignment_id

    assignment_id = env.get_assignment_id()
    default_worksites = env.get_default_worksites()
    url = "/assignments/%s/worksites/batchUpdateLabels" % assignment_id
  
    print("Create 3 Worksites")
    response = self.client.post(url, headers=
    {
      "Authorization": self.jwt,
      "Content-Type": "application/json"
    }, json=default_worksites
    )

    body = json.loads(response.text)
    message = "!!AssignmentId= {1}: @@Worksites= {0}".format(body['assignmentWorksites'], assignment_id)

    print(message)

  @seq_task(2)
  def get_worksites(self):
    global assignment_id, worksite_id

    url = "/assignments/%s/worksites" % assignment_id

    print("Get Worksites")
    response = self.client.get(url, headers=
    {
      "Authorization": self.jwt,
      "Content-Type": "application/json"
    })
    body = json.loads(response.text)
    if len(body['assignmentWorksites']) > 0:
      worksite_id = body['assignmentWorksites'][0]['worksiteId']

    message = "Worksite count = {0}".format(len(body['assignmentWorksites']))
    message2 = "AssignmentId = {1} Worksite Id = {0}".format(body['assignmentWorksites'][0]['worksiteId'], assignment_id)
    
    print(message)
    print(message2)
    
  @seq_task(3)
  def createShift(self):
    global assignment_id, worksite_id

    start_date = "2019-08-02"
    url = "/assignments/%s/shifts" % assignment_id
    
    for x in range(100):
      print("Create A Shift #{0}".format(x))
      response = self.client.post(url, headers=
      {
        "Authorization": self.jwt,
        "Content-Type": "application/json"
      }, json=
      {
        "startDate": start_date,
        "status": "Tentative",
        "worksites":[{
          "worksiteId": worksite_id
        }]
      })
      body = json.loads(response.text)
      message = "Shift = {0}".format(body)

      print(message)
      print("100 Shifts Created")

  @seq_task(4)
  def get_shifts(self):
    global assignment_id, shift_id, delete_shifts

    url = "/assignments/%s/shifts" % assignment_id

    print("Get Shifts")
    response = self.client.get(url, headers=
    {
      "Authorization": self.jwt,
      "Content-Type": "application/json"
    })
    
    body = json.loads(response.text)
    message = "Shifts count = {0}".format(len(body['shifts']))
    
    shifts = body['shifts']
    shift_id = shifts[0]['id']
    for s in shifts:
      delete_shifts.append(s['id'])
    
    print(message)
    print(delete_shifts)

class WebsiteUser(HttpLocust):
    response = env.get_tokensecrets("stage")
    target = response[0]
    
    task_set = GetShifts
    host = target
    min_wait = 1000
    max_wait = 3000