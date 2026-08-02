import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzg2MzA2NTg2fQ.-03_K8a9MiKMo-mhB1k7VmqA_JbfrsHkghe_HRd3ysM"}

requisicao =requests.get("http://localhost:8000/auth/refresh", headers=headers)

print(requisicao)
print(requisicao.json())
print(requisicao.status_code)
