import requests

url = "http://127.0.0.1:5000/profesores/" 

nuevo_usuario = {
    "nombre": "Admin",
    "apellido": "Test",
    "email": "admin@test.com",
    "password": "password123"
}

response = requests.post(url, json=nuevo_usuario)
print(response.status_code)
print(response.json())