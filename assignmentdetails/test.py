def identity_login(self):
    global brand, provider, password

    identity_service = "https://api.dev.pde.aws.chgit.com/identity-service"  # stage
    url = "%s/v1/login" % identity_service
    response = self.client.post(url, headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "correlation-object": '{"correlationId": "%s"}' % guid,
        "brand": "%s" % brand
    }, json={
        "username": provider,
        "password": password
    }
    )
    json_res = response.json()
    body = json_res['result']
    jwt = body['jwt']
    print(json_res)
    # self.sessionToken = body[sessionToken]
    # print(self.okta_id)
    self.okta_id = jwt['sub']
    print(self.okta_id)

    # okta_url = "https://chghealthcare.oktapreview.com/oauth2/auskmtjacfEi8ffM60h7"
    # endpoint = "https://chghealthcare.oktapreview.com"
    # apiKey = "00qaFu9yrcsmf3i-8-ry-UiWYorHHiRUNhP-i8Nd0n"

    # url2 = endpoint + "/api/v1/apps/?q=PDE UI SPA application"
    # appLookup = self.client.get(url2, headers={
    #     "Content-Type": "application/json",
    #     "Authorization": "SSWS %s" % apiKey
    # }
    # )
