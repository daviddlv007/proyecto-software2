import os
import requests
import zipfile

# =========================
# 1️⃣ Configuración
# =========================
backend_dir = "backend"
os.makedirs(backend_dir, exist_ok=True)

url = "https://start.spring.io/starter.zip"
params = {
    "type": "maven-project",
    "language": "java",
    "bootVersion": "3.4.10.RELEASE",  # versión compatible
    "groupId": "com.supermercado",
    "artifactId": "backend",
    "name": "backend",
    "packageName": "com.supermercado",
    "dependencies": "web,data-jpa,h2"  # solo dependencias básicas
}

zip_path = os.path.join(backend_dir, "backend.zip")

# =========================
# 2️⃣ Descargar ZIP
# =========================
print("Descargando proyecto Spring Boot...")
r = requests.get(url, params=params)
if r.status_code != 200:
    print("Error al descargar Spring Boot:", r.status_code)
    print(r.text[:500])
    exit(1)

with open(zip_path, "wb") as f:
    f.write(r.content)

# =========================
# 3️⃣ Extraer ZIP
# =========================
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(backend_dir)
os.remove(zip_path)

print("✅ Proyecto backend vacío creado correctamente en:", backend_dir + "/backend")
print("Para levantarlo:")
print(f"cd {backend_dir}/backend && ./mvnw spring-boot:run")
