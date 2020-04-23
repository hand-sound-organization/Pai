import requests

response = requests.get("http://127.0.0.1:5000/app/login")
print(response.headers)
print(response.request)
print(response.json()['isTrue'])
