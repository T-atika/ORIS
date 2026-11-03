import requests

url = "http://127.0.0.1:5000/notes"
base = "http://127.0.0.1:5000"

r = requests.post(url, json={"author": "Ivan", "text": "Hi"})
print(r.status_code, r.json())

r = requests.post(url, json={"text": "Hi"})
print(r.status_code, r.json())

r = requests.post(url, json={"author": " ", "text": "x"})
print(r.status_code, r.json())

r = requests.post(url, json={"author": "Maria", "text": "Second"})
print(r.status_code, r.json())

r = requests.post(f"{url}/1/like")
print(r.status_code, r.json())

r = requests.post(f"{url}/1/like")
print(r.status_code, r.json())

r = requests.post(f"{url}/2/like")
print(r.status_code, r.json())

r = requests.post(f"{url}/999/like")
print(r.status_code, r.json())

r = requests.put(f"{url}/1", json={"author": "Petr", "text": "New"})
print(r.status_code, r.json())

r = requests.put(f"{url}/999", json={"author": "Petr", "text": "New"})
print(r.status_code, r.json())

r = requests.put(f"{url}/1", json={"author": "Petr"})
print(r.status_code, r.json())

r = requests.patch(f"{url}/1", json={"text": "Only text updated"})
print(r.status_code, r.json())

r = requests.patch(f"{url}/999", json={"text": "New"})
print(r.status_code, r.json())

r = requests.patch(f"{url}/1", json={"text": ""})
print(r.status_code, r.json())

r = requests.get(url)
print(r.status_code, r.json())

r = requests.get(f"{url}?author=Petr")
print(r.status_code, r.json())

r = requests.get(f"{url}?limit=2&offset=0")
print(r.status_code, r.json())

r = requests.get(f"{url}?limit=abc")
print(r.status_code, r.json())

r = requests.get(f"{url}?limit=200")
print(r.status_code, r.json())

r = requests.get(f"{url}?offset=-1")
print(r.status_code, r.json())

r = requests.get(f"{url}?sort=likes&order=desc")
print(r.status_code, r.json())

r = requests.get(f"{url}?sort=id&order=asc")
print(r.status_code, r.json())

r = requests.get(f"{url}?sort=invalid")
print(r.status_code, r.json())

r = requests.get(f"{url}?order=invalid")
print(r.status_code, r.json())

r = requests.get(f"{base}/authors")
print(r.status_code, r.json())

r = requests.delete(url, params={"author": "Petr"})
print(r.status_code, r.json())

r = requests.delete(url, params={"author": "Petr"})
print(r.status_code, r.json())

r = requests.delete(url)
print(r.status_code, r.json())

r = requests.delete(url, params={"author": "   "})
print(r.status_code, r.json())