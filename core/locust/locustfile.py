from locust import HttpUser, task, between


class QuickStartUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def initial_task(self):
        self.client.get("/initiate-task")
    
    def not_found(self):
        self.client.get("/not_found")
