from locust import HttpUser, task, between
from locust import events
import requests

token = requests.post("http://111.88.153.111/api/auth/login", json={"username":"pgdev14", "password": "123"}).json().get("access_token")

print(token)
class APIUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    @task
    def get_user(self):
        with self.client.get("/api/authors", headers={"Authorization": f"Bearer {token}"}, catch_response=True) as response:
            # Validate response body
#            print(response)
            if response.status_code == 200:
#                response.mark_success()
                data = response.json()
#                if data.get("id") == 123:
#                    response.mark_success()
#                else:
#                    response.mark_failure("Unexpected user ID")
#            else:
#                response.mark_failure(f"Expected 200, got {response.status_code}")
    @task
    def get_attrubute(self):
        with self.client.post("/api/attribute", json={'text': 'privet', 'k':10, "threshold": 0.5}, headers={"Authorization": f"Bearer {token}"}, catch_response=True) as response:
             #print(response.text)
            pass
    #@task
    #def create_user(self):
    #    payload = {"name": "Test User", "email": "test@example.com"}
    #    response = self.client.post("/api/users", json=payload)
    #    assert response.status_code == 201, f"Failed: {response.text}"
