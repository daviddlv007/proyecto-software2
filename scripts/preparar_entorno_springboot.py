import os
import subprocess

def run(cmd, check=True):
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

print("=== 1️⃣ Actualizando sistema ===")
run("sudo apt update && sudo apt upgrade -y")

print("=== 2️⃣ Instalando Java 17, Maven y herramientas básicas ===")
run("sudo apt install -y openjdk-17-jdk maven unzip curl git python3 python3-pip python3-requests")

print("=== 3️⃣ Configurando JAVA_HOME ===")
java_home = "/usr/lib/jvm/java-17-openjdk-amd64"
bashrc = os.path.expanduser("~/.bashrc")

# Evitar duplicar entradas
with open(bashrc, "r") as f:
    content = f.read()
if f'export JAVA_HOME={java_home}' not in content:
    with open(bashrc, "a") as f:
        f.write(f"\nexport JAVA_HOME={java_home}\n")
        f.write("export PATH=$JAVA_HOME/bin:$PATH\n")

# Aplicar para la sesión actual
os.environ["JAVA_HOME"] = java_home
os.environ["PATH"] = f"{java_home}/bin:" + os.environ["PATH"]
print(f"JAVA_HOME configurado en {java_home}")

print("=== 4️⃣ Comprobando instalaciones ===")
run("java -version", check=False)
run("mvn -version", check=False)
run("python3 --version", check=False)
run("python3 -m pip show requests | grep Version", check=False)

print("\n=== ✅ Entorno preparado correctamente ===")
print("Ahora puedes levantar tu backend de Spring Boot con:")
print("cd ruta/a/tu/backend && ./mvnw spring-boot:run")
