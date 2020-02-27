from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task
import uuid
import env
import json

# ugly globals
brand = "comphealth"

# hard code token for now
token = "eyJraWQiOiJvQlZrZklSNXA4Q19zRzdpMGtnVFJiSTg5b3lZUS1fRTdFMEwwYS1UdG1nIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULnlDLVdwMFAyOE5RVnBsUFJ2NmNQdFNuVVVPWTZ3d0VBa2VJQzItQkZuUmMiLCJpc3MiOiJodHRwczovL2NoZ2hlYWx0aGNhcmVzdGFnZS5va3RhcHJldmlldy5jb20vb2F1dGgyL2F1c25mOW11YXE5T1BQMUxCMGg3IiwiYXVkIjoiYXBpOi8vZGVmYXVsdCIsImlhdCI6MTU3NjA4OTU3OSwiZXhwIjoxNTc2MDkzMTc5LCJjaWQiOiIwb2FobjJvZjRwSnVIZmpBeDBoNyIsInVpZCI6IjAwdW81NzFuYjlQRko3VnptMGg3Iiwic2NwIjpbImdsb2JhbF90cmFuc2FjdGlvbmFsX2VtYWlsX3NlcnZpY2UiLCJwZGVfcHJvdmlkZXIiLCJvcGVuaWQiXSwic3ViIjoiY2hncGRldGVhbSt3b3Jrc2NoZWR1bGVsaXN0QGdtYWlsLmNvbSJ9.ZnSYC3H4P7tJ5X_6H98PBgIsN-DxcVP95PSaH5NEyU1rCiSi2TvG50Ydf32YF96uJ1-ixSFT28UOvTkRwXq1KUYWfResg4uo1aywQQNdH73qAyIH8Yr-W-BnmENPnAQerbOycXUCrAvikCKf6U8WG9Mb7S2njw3E6mVCSn9_Ml8F6UN35ML6fllUI7SgTvFzuU0TZEM5g0bpQKW5bZ24lYivJ1E0Yk521fU2w6NUIaJzuoV_HQQRljgoGc0DbGUZ0xDVDKZD3UyW_iUsppZMelJ7kE-UNapXgKHcwfvgRwiEf2-PTKjMliRFLUW2aDp-nzB-O1v20tng8GnCNXxrIg"
jwt = "Bearer {0}".format(token)


class GetWorksiteShifts(TaskSequence):

    @seq_task(1)
    def get_confirmed_worksites(self):
        global jwt, guid, brand
        # GET / providers/%s/assignment/schedule

        results = env.get_target("stage")
        self.okta_id = results[1]

        url = "/providers/%s/assignment/schedule" % self.okta_id
        response = self.client.get(url, headers={
            "Authorization": jwt,
            "brand": brand
        }
        )
        json_body = json.loads(response.text)
        print("Response", json_body)
        result = json_body['result']
        scheduled_worksites = result['scheduledWorksites']
        worksite = scheduled_worksites[0]
        self.worksite_id = worksite['worksiteId']
        print("worksite Id ", self.worksite_id)
        self.assignment_id = worksite['assignmentId']
        print("AssignmentId ", self.assignment_id)

    @seq_task(2)
    def get_worksite_shifts(self):
        global jwt, brand
        # Get /providers/{{okta_id}}/assignment/a0Cc000000QOU51EAH/worksite/001c0000020vRKqAAM/shifts

        url = "/providers/{0}/assignment/{1}/worksite/{2}/shifts".format(
            self.okta_id, self.assignment_id, self.worksite_id)
        print(url)
        response = self.client.get(url, headers={
            "Authorization": jwt,
            "brand": brand
        }
        )
        json_body = json.loads(response.text)
        result = json_body['result']
        print("RESULT", result)


class WebsiteUser(HttpLocust):
    response = env.get_target("stage")
    target = response[0]

    task_set = GetWorksiteShifts
    host = target
    min_wait = 1000
    max_wait = 3000
