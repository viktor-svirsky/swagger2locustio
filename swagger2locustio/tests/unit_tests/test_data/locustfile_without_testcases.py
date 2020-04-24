import os
from base64 import b64encode
from locust import HttpLocust, TaskSet, between, task

API_PREFIX = ""



class Tests(TaskSet):

    def on_start(self):

        pass



class WebsiteUser(HttpLocust):
    task_set = Tests
    wait_time = between(5.0, 9.0)

    host = "api.example.com"
