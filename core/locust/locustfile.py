from locust import HttpUser, task, between


class QuickStartUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def initial_task(self):
        self.client.get("/initiate-task")

    @task
    def not_found(self):
        self.client.get("/not_found")
    
    @task
    def fetch_tehran_weather(self):
        self.client.get("/fetch-tehran-weather")
    
    @task
    def tasks_list(self):
        self.client.get("/tasks")
