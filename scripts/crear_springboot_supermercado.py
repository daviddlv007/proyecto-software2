import os
import requests
import zipfile

# =========================
# Configuración general
# =========================
backend_dir = "backend"
os.makedirs(backend_dir, exist_ok=True)

# =========================
# Paso 1: Descargar Spring Boot vacío
# =========================
url = "https://start.spring.io/starter.zip"
params = {
    "type": "maven-project",
    "language": "java",
    "bootVersion": "3.5.6",
    "groupId": "com.supermercado",
    "artifactId": "backend",
    "name": "backend",
    "packageName": "com.supermercado",
    "dependencies": "web,data-jpa,h2,lombok"
}

zip_path = os.path.join(backend_dir, "backend.zip")

print("Descargando proyecto Spring Boot vacío...")
r = requests.get(url, params=params)
if r.status_code != 200:
    print("Error al descargar Spring Boot:", r.status_code)
    exit(1)

with open(zip_path, "wb") as f:
    f.write(r.content)

with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(backend_dir)
os.remove(zip_path)
print("Proyecto Spring Boot descargado y extraído en:", backend_dir)

# =========================
# Paso 2: Crear pom.xml moderno con GraphQL oficial y Lombok
# =========================
pom_path = os.path.join(backend_dir, "pom.xml")

pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                             https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.5.6</version>
        <relativePath/>
    </parent>

    <groupId>com.supermercado</groupId>
    <artifactId>backend</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>backend</name>
    <description>Backend para Supermercado con GraphQL</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-graphql</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <version>1.18.30</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
"""

with open(pom_path, "w", encoding="utf-8") as f:
    f.write(pom_content)
print("✅ pom.xml moderno creado con GraphQL oficial y Lombok")

# =========================
# Paso 3: Crear estructura de paquetes
# =========================
base_java = os.path.join(backend_dir, "src", "main", "java", "com", "supermercado")
model_dir = os.path.join(base_java, "model")
repo_dir = os.path.join(base_java, "repository")
resolver_dir = os.path.join(base_java, "resolver")
os.makedirs(model_dir, exist_ok=True)
os.makedirs(repo_dir, exist_ok=True)
os.makedirs(resolver_dir, exist_ok=True)
print("Estructura de paquetes creada: model, repository, resolver")

# =========================
# Paso 4: Crear application.properties
# =========================
resources_dir = os.path.join(backend_dir, "src", "main", "resources")
os.makedirs(resources_dir, exist_ok=True)
app_props_path = os.path.join(resources_dir, "application.properties")
with open(app_props_path, "w") as f:
    f.write("""spring.h2.console.enabled=true
spring.datasource.url=jdbc:h2:mem:testdb
spring.jpa.hibernate.ddl-auto=update
server.port=8080
spring.graphql.graphiql.enabled=true
""")  # línea schema.locations eliminada
print("✅ application.properties creado")

# =========================
# Paso 5: Crear modelos con Lombok y JPA
# =========================
models = {
    "Categoria": {"nombre": "String", "descripcion": "String"},
    "Producto": {"nombre": "String", "descripcion": "String", "imagenUrl": "String", "precio": "Double", "stock": "Integer", "categoria": "Categoria"},
    "Cliente": {"nombre": "String", "correo": "String", "telefono": "String"},
    "Usuario": {"nombre": "String", "correo": "String", "contrasena": "String"},
    "Venta": {"cliente": "Cliente", "fecha": "LocalDateTime", "total": "Double"},
    "DetalleVenta": {"venta": "Venta", "producto": "Producto", "cantidad": "Integer", "precioUnitario": "Double"}
}

for name, fields in models.items():
    path = os.path.join(model_dir, f"{name}.java")
    with open(path, "w") as f:
        f.write("package com.supermercado.model;\n")
        f.write("import jakarta.persistence.*;\n")
        f.write("import lombok.Data;\n")
        if "LocalDateTime" in fields.values():
            f.write("import java.time.LocalDateTime;\n")
        for t in fields.values():
            if t not in ["String","Integer","Double","LocalDateTime"]:
                f.write(f"import com.supermercado.model.{t};\n")
        f.write("\n@Data\n@Entity\n")
        f.write(f"public class {name} {{\n")
        f.write("    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)\n")
        f.write("    private Long id;\n")
        for field_name, type_ in fields.items():
            if type_ in models:
                f.write(f"    @ManyToOne\n")
                f.write(f"    private {type_} {field_name};\n")
            else:
                f.write(f"    private {type_} {field_name};\n")
        f.write("}\n")
print("✅ Modelos creados con Lombok y JPA")

# =========================
# Paso 6: Crear repositorios
# =========================
for name in models.keys():
    path = os.path.join(repo_dir, f"{name}Repository.java")
    with open(path, "w") as f:
        f.write(f"package com.supermercado.repository;\n")
        f.write("import org.springframework.data.jpa.repository.JpaRepository;\n")
        f.write(f"import com.supermercado.model.{name};\n\n")
        f.write(f"public interface {name}Repository extends JpaRepository<{name}, Long> {{}}\n")
print("✅ Repositorios creados")

# =========================
# Paso 7: Crear resolvers GraphQL con CRUD completo
# =========================
for name, fields in models.items():
    path = os.path.join(resolver_dir, f"{name}Resolver.java")
    with open(path, "w") as f:
        f.write("package com.supermercado.resolver;\n")
        f.write("import org.springframework.stereotype.Controller;\n")
        f.write("import org.springframework.graphql.data.method.annotation.QueryMapping;\n")
        f.write("import org.springframework.graphql.data.method.annotation.MutationMapping;\n")
        f.write("import org.springframework.graphql.data.method.annotation.Argument;\n")
        f.write("import java.util.List;\n")
        if "LocalDateTime" in fields.values():
            f.write("import java.time.LocalDateTime;\n")
        f.write(f"import com.supermercado.model.{name};\n")
        f.write(f"import com.supermercado.repository.{name}Repository;\n")
        for t in fields.values():
            if t in models and t != name:
                f.write(f"import com.supermercado.repository.{t}Repository;\n")
        f.write("\n@Controller\n")
        f.write(f"public class {name}Resolver {{\n")
        f.write(f"    private final {name}Repository repository;\n")
        for field_name, t in fields.items():
            if t in models and t != name:
                f.write(f"    private final {t}Repository {field_name}Repository;\n")
        # Constructor
        f.write(f"\n    public {name}Resolver({name}Repository repository")
        for field_name, t in fields.items():
            if t in models and t != name:
                f.write(f", {t}Repository {field_name}Repository")
        f.write(") {\n")
        f.write("        this.repository = repository;\n")
        for field_name, t in fields.items():
            if t in models and t != name:
                f.write(f"        this.{field_name}Repository = {field_name}Repository;\n")
        f.write("    }\n\n")
        # Query
        f.write(f"    @QueryMapping\n    public List<{name}> all{name}s() {{\n")
        f.write("        return repository.findAll();\n    }\n\n")
        # Mutaciones CRUD
        f.write(f"    @MutationMapping\n    public {name} create{name}(")
        args = []
        for field_name, t in fields.items():
            if t in ["String","Double","Integer","LocalDateTime"]:
                args.append(f"@Argument {t} {field_name}")
            else:
                args.append(f"@Argument Long {field_name}Id")
        f.write(", ".join(args))
        f.write(") {\n")
        f.write(f"        {name} obj = new {name}();\n")
        for field_name, t in fields.items():
            if t in ["String","Double","Integer","LocalDateTime"]:
                f.write(f"        obj.set{field_name[0].upper()+field_name[1:]}({field_name});\n")
            else:
                f.write(f"        obj.set{field_name[0].upper()+field_name[1:]}({field_name}Repository.findById({field_name}Id).orElseThrow());\n")
        f.write("        return repository.save(obj);\n    }\n\n")

        # Update
        f.write(f"    @MutationMapping\n")
        f.write(f"    public {name} update{name}(@Argument Long id")
        for field_name, t in fields.items():
            if t in ["String","Double","Integer","LocalDateTime"]:
                f.write(f", @Argument {t} {field_name}")
            elif t in models:
                f.write(f", @Argument Long {field_name}Id")
        f.write(") {\n")
        f.write(f"        {name} obj = repository.findById(id).orElseThrow();\n")
        for field_name, t in fields.items():
            if t in ["String","Double","Integer","LocalDateTime"]:
                f.write(f"        if ({field_name} != null) obj.set{field_name[0].upper()+field_name[1:]}({field_name});\n")
            elif t in models:
                f.write(f"        if ({field_name}Id != null) obj.set{field_name[0].upper()+field_name[1:]}({field_name}Repository.findById({field_name}Id).orElseThrow());\n")
        f.write("        return repository.save(obj);\n    }\n\n")

        # Delete
        f.write(f"    @MutationMapping\n")
        f.write(f"    public Boolean delete{name}(@Argument Long id) {{\n")
        f.write("        repository.deleteById(id);\n")
        f.write("        return true;\n")
        f.write("    }\n")

        f.write("}\n")
print("✅ Resolvers CRUD completos creados")

# =========================
# Paso 8: Crear carpeta graphql y schema.graphqls con CRUD completo
# =========================
graphql_dir = os.path.join(resources_dir, "graphql")
os.makedirs(graphql_dir, exist_ok=True)

schema_path = os.path.join(graphql_dir, "schema.graphqls")
with open(schema_path, "w") as f:
    f.write("""type Categoria { id: ID! nombre: String descripcion: String }
type Producto { id: ID! nombre: String descripcion: String imagenUrl: String precio: Float stock: Int categoria: Categoria }
type Cliente { id: ID! nombre: String correo: String telefono: String }
type Usuario { id: ID! nombre: String correo: String contrasena: String }
type Venta { id: ID! cliente: Cliente fecha: String total: Float }
type DetalleVenta { id: ID! venta: Venta producto: Producto cantidad: Int precioUnitario: Float }

type Query {
  allCategorias: [Categoria]
  allProductos: [Producto]
  allClientes: [Cliente]
  allUsuarios: [Usuario]
  allVentas: [Venta]
  allDetalleVentas: [DetalleVenta]
}

type Mutation {
  createCategoria(nombre: String!, descripcion: String): Categoria
  updateCategoria(id: ID!, nombre: String, descripcion: String): Categoria
  deleteCategoria(id: ID!): Boolean

  createProducto(nombre: String!, descripcion: String, imagenUrl: String, precio: Float!, stock: Int, categoriaId: ID!): Producto
  updateProducto(id: ID!, nombre: String, descripcion: String, imagenUrl: String, precio: Float, stock: Int, categoriaId: ID): Producto
  deleteProducto(id: ID!): Boolean

  createCliente(nombre: String!, correo: String!, telefono: String): Cliente
  updateCliente(id: ID!, nombre: String, correo: String, telefono: String): Cliente
  deleteCliente(id: ID!): Boolean

  createUsuario(nombre: String!, correo: String!, contrasena: String!): Usuario
  updateUsuario(id: ID!, nombre: String, correo: String, contrasena: String): Usuario
  deleteUsuario(id: ID!): Boolean

  createVenta(clienteId: ID!, fecha: String, total: Float!): Venta
  updateVenta(id: ID!, clienteId: ID, fecha: String, total: Float): Venta
  deleteVenta(id: ID!): Boolean

  createDetalleVenta(ventaId: ID!, productoId: ID!, cantidad: Int!, precioUnitario: Float!): DetalleVenta
  updateDetalleVenta(id: ID!, ventaId: ID, productoId: ID, cantidad: Int, precioUnitario: Float): DetalleVenta
  deleteDetalleVenta(id: ID!): Boolean
}
""")
print("✅ schema.graphqls CRUD completo creado en /graphql")

print("\n🎉 Backend de supermercado listo y compilable con Spring Boot 3.5.6 y GraphQL")
print(f"Para levantarlo: cd {backend_dir} && chmod +x mvnw && ./mvnw spring-boot:run")
