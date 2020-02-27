import os
import sys


def get_target(environment):
    if environment == "stage":
        target = "https://api.stage.pde.aws.chgit.com/providers-service"
        okta_id = "00uo571nb9PFJ7Vzm0h7"
    else:
        target = "https://api.dev.pde.aws.chgit.com/providers-service"
        okta_id = "00unycwyd7y7TymHN0h7"
    return (target, okta_id)

    # aws sdk to talk to ssm for secrets
