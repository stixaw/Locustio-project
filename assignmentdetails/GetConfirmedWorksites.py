from locust import HttpLocust, TaskSet, task, TaskSequence, seq_task
import uuid
import env
import json

# ugly globals
brand = "comphealth"

# hard code token for now
token = "eyJraWQiOiJvQlZrZklSNXA4Q19zRzdpMGtnVFJiSTg5b3lZUS1fRTdFMEwwYS1UdG1nIiwiYWxnIjoiUlMyNTYifQ.eyJ2ZXIiOjEsImp0aSI6IkFULmhxc2RFemowbFl2YWFaU1RDenJrNzBPakJlXy0xbldFZjQ1cmxxUVBiUUUiLCJpc3MiOiJodHRwczovL2NoZ2hlYWx0aGNhcmVzdGFnZS5va3RhcHJldmlldy5jb20vb2F1dGgyL2F1c25mOW11YXE5T1BQMUxCMGg3IiwiYXVkIjoiYXBpOi8vZGVmYXVsdCIsImlhdCI6MTU3NjA4NTIzMywiZXhwIjoxNTc2MDg4ODMzLCJjaWQiOiIwb2FobjJvZjRwSnVIZmpBeDBoNyIsInVpZCI6IjAwdW81NzFuYjlQRko3VnptMGg3Iiwic2NwIjpbImdsb2JhbF90cmFuc2FjdGlvbmFsX2VtYWlsX3NlcnZpY2UiLCJwZGVfcHJvdmlkZXIiLCJvcGVuaWQiXSwic3ViIjoiY2hncGRldGVhbSt3b3Jrc2NoZWR1bGVsaXN0QGdtYWlsLmNvbSJ9.z3Hm9r9tfCE4zBip5v4eEb1xXvfdCii2eS7Ql_QXOpsSL8Sk22ApG3st7hT6naKUurp-pj5KJsh6v2JWU0eAq4auA-rMUX_xcds4rouNO5_HNscdUQm4S95xj9AsdaYi0ZOIZrnCACu7jBOlEOaYzVUFFknvU98aQhI-hfrOCUdzyUujy9rDwa20yAaPFsT6gU7t3XlM7QqHE5C7KaTskknt4UjLh9HnWAeq2sbFkhHLZKJlc41WTvW5dp-810OZU1zIqepw20Pi9PnMWW3NrSRrt3D3RK3qvp76Tpi8fOSd_wVKXqsFLi3wWn8ppqJsGxZ9vni1MPPwvG7JF2kUTQ"
jwt = "Bearer {0}".format(token)


class GetConfirmedWorksites(TaskSequence):

    @seq_task(1)
    def get_confirmed_worksites(self):
        global jwt, guid, brand
        # GET / providers/%s/assignment/schedule

        results = env.get_target("stage")
        okta_id = results[1]

        url = "/providers/%s/assignment/schedule" % okta_id
        print("URL", url)
        response = self.client.get(url, headers={
            "Authorization": jwt,
            # "correlation-object": {"correlationId": guid},
            "brand": brand
        }
        )
        body = json.loads(response.text)
        print("Response", body)


class WebsiteUser(HttpLocust):
    response = env.get_target("stage")
    target = response[0]

    task_set = GetConfirmedWorksites
    host = target
    min_wait = 1000
    max_wait = 3000
