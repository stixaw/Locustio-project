# Locustio

Locustio is a tool for running api load testing

## Prerequisites

for Python 3:
```bash
$ python3 -m pip install locustio
```

MacOS:

Install Homebrew
Inastll libev

```bash
brew install libev
```
for Python 3:
```bash
$ python3 -m pip install locustio
```

Windows:
install python 3

install pip3

install Locustio:

for Python 3:
```bash
$ python3 -m pip3 install locustio
```

## Usage

if you are working in the locustio directory make sure you can see the .py files for tests:

To call the Tests using the UI from within locustio directory:
```bash
locust -f GetShifts.py
```

Running with master and slaves:
```bash
locust -f my_locustfile.py --slave --master-host=192.168.0.14
```

Running without UI:
```bash
locust -f locust_files/my_locust_file.py --no-web -c 1000 -r 100
```

Running Locust distributed without the web UI, you should specify the --expect-slaves

Running with Docker Image:

First ensure your docker.yml file has the correct environment for testing:
DOCKER_ENV=feature or dev, stage
and determine what test you want to run in this session:
command: -f /mnt/locust/workschedule/Create_Shift.py --master


Second, if you are doing feature branch in the env.py you need to set the feature branch:
    if environment == "feature":
        target = "https://pde-3593-use-sequeliz--chg-work-schedule-service.feature.platform.aws.chgit.com" 

Starting docker session with ui and 1 worker:
```
docker-compose up --scale worker=1
```

go to http://localhost:8089/ to start the scenario:
Standard load is 20 users 10 hatch rate

Running with Docker:

https://docs.locust.io/en/stable/running-locust-docker.html#running-locust-docker


## Retrieve Test statistics in CSV format
You can run Locust with a flag which will periodically save two CSV files. This is particularly useful if you plan on running Locust in an automated way with the --no-web flag:
```bash
$ locust -f examples/basic.py --csv=example --no-web -t10m
```
The files will be named example_distribution.csv and example_requests.csv (when using --csv=example) and mirror Locust’s built in stat pages.

## Additional Resources
1. https://docs.locust.io/en/stable/what-is-locust.html


