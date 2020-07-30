import uuid
import random

def get_assignment_id():
    a_uuid = uuid.uuid4()
    assignment_id = "test-{0}".format(a_uuid)
    return assignment_id


def get_worksite_id():
    s_uuid = uuid.uuid4()
    worksite_id = "test-{0}".format(s_uuid)
    return worksite_id


def get_worksite_label():
    ADJECTIVE = ["livid", "lemony", "acrid", "testy",
                 "beautiful", "curvy", "party", "awful"]
    ANIMAL = ["alpaca", "cat", "cattle", "chicken", "dog", "donkey",
              "ferret", "guppy", "goldfish", "horse", "koi", "llama", "sheep", "yak"]
    word1 = random.choice(ADJECTIVE)
    word2 = random.choice(ANIMAL)
    worksite_label = "{0} {1}".format(word1, word2)
    return worksite_label


def get_default_worksites():
    worksite_id1 = get_worksite_id()
    worksite_id2 = get_worksite_id()
    worksite_id3 = get_worksite_id()

    default_worksites = {
        "assignmentWorksites": [
            {
                "worksiteId": worksite_id1,
                "primary": True,
                "label": get_worksite_label()
            },
            {
                "worksiteId": worksite_id2,
                "primary": False,
                "label": get_worksite_label()
            },
            {
                "worksiteId": worksite_id3,
                "primary": False,
                "label": get_worksite_label()
            }
        ]
    }
    return default_worksites

