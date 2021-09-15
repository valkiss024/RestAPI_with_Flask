import requests

BASE_URL = "http://127.0.0.1:5000/"

payload = {"first_name": "Val", "last_name": "Kiss", "age": 26, "email": "test@test.com"}
response = requests.patch(BASE_URL + "students/1", params=payload)
print(response.text) 
