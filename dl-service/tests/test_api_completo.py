#!/usr/bin/env python3
"""
TEST COMPLETO - DL SERVICE API
Prueba todos los endpoints del microservicio de Deep Learning

Requisitos:
    pip install requests pillow colorama

Uso:
    python test_api_completo.py
"""

import requests
import json
import time
import sys
from io import BytesIO
from pathlib import Path
from PIL import Image
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Configuración
BASE_URL = "http://localhost:8082"
TIMEOUT = 30


class TestDLService:
    """Test completo para DL Service API"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.tests_passed = 0
        self.tests_failed = 0
        
    def print_header(self, text: str):
        print(f"\n{'='*70}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{text:^70}")
        print(f"{'='*70}\n")
        
    def print_success(self, text: str):
        print(f"{Fore.GREEN}✅ {text}")
        
    def print_error(self, text: str):
        print(f"{Fore.RED}❌ {text}")
        
    def print_info(self, text: str):
        print(f"{Fore.BLUE}ℹ️  {text}")
        
    def print_json(self, data: dict, max_lines: int = 30):
        """Imprime JSON con límite de líneas"""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        lines = json_str.split('\n')
        if len(lines) > max_lines:
            print(f"{Fore.WHITE}{''.join(lines[:max_lines])}")
            print(f"{Fore.YELLOW}... ({len(lines) - max_lines} líneas más)")
        else:
            print(f"{Fore.WHITE}{json_str}")
    
    def create_test_image(self) -> BytesIO:
        """Crea una imagen de prueba (banana)"""
        img = Image.new('RGB', (224, 224), color='yellow')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer
    
    # ==========================================
    # TEST 1: Conexión y Health Check
    # ==========================================
    def test_health(self) -> bool:
        self.print_header("TEST 1: HEALTH CHECK")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Servicio disponible: {data.get('service', 'N/A')}")
                self.print_info(f"Modelo: {data.get('modelo', 'N/A')}")
                self.tests_passed += 1
                return True
            else:
                self.print_error(f"Health check falló: {response.status_code}")
                self.tests_failed += 1
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_error(f"No se puede conectar a {self.base_url}")
            self.print_info("Ejecuta: npm run dev")
            self.tests_failed += 1
            return False
        except Exception as e:
            self.print_error(f"Error: {str(e)}")
            self.tests_failed += 1
            return False
    
    # ==========================================
    # TEST 2: Listar Productos
    # ==========================================
    def test_productos(self):
        self.print_header("TEST 2: GET /api/productos")
        #!/usr/bin/env python3
        """
        TEST COMPLETO - DL SERVICE API
        Prueba todos los endpoints del microservicio de Deep Learning

        Requisitos:
            pip install requests pillow colorama

        Uso:
            python3 test_api_completo.py
        """

        import requests
        import json
        import time
        import sys
        from io import BytesIO
        from pathlib import Path
        from PIL import Image
        from colorama import init, Fore, Style

        # Inicializar colorama
        init(autoreset=True)

        # Configuración
        BASE_URL = "http://localhost:8082"
        TIMEOUT = 30


        class TestDLService:
            """Test completo para DL Service API"""
    
            def __init__(self):
                self.base_url = BASE_URL
                self.tests_passed = 0
                self.tests_failed = 0
        
            def print_header(self, text: str):
                print(f"\n{'='*70}")
                print(f"{Fore.CYAN}{Style.BRIGHT}{text:^70}")
                print(f"{'='*70}\n")
        
            def print_success(self, text: str):
                print(f"{Fore.GREEN}✅ {text}")
        
            def print_error(self, text: str):
                print(f"{Fore.RED}❌ {text}")
        
            def print_info(self, text: str):
                print(f"{Fore.BLUE}ℹ️  {text}")
        
            def print_json(self, data: dict, max_lines: int = 30):
                """Imprime JSON con límite de líneas"""
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                lines = json_str.split('\n')
                if len(lines) > max_lines:
                    print(f"{Fore.WHITE}{''.join(lines[:max_lines])}")
                    print(f"{Fore.YELLOW}... ({len(lines) - max_lines} líneas más)")
                else:
                    print(f"{Fore.WHITE}{json_str}")
    
            def create_test_image(self) -> BytesIO:
                """Crea una imagen de prueba (banana)"""
                img = Image.new('RGB', (224, 224), color='yellow')
                buffer = BytesIO()
                img.save(buffer, format='JPEG')
                buffer.seek(0)
                return buffer
    
            # ==========================================
            # TEST 1: Conexión y Health Check
            # ==========================================
            def test_health(self) -> bool:
                self.print_header("TEST 1: HEALTH CHECK")
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
            
                    if response.status_code == 200:
                        data = response.json()
                        self.print_success(f"Servicio disponible: {data.get('service', 'N/A')}")
                        self.print_info(f"Modelo: {data.get('modelo', 'N/A')}")
                        self.tests_passed += 1
                        return True
                    else:
                        self.print_error(f"Health check falló: {response.status_code}")
                        self.tests_failed += 1
                        return False
                
                except requests.exceptions.ConnectionError:
                    self.print_error(f"No se puede conectar a {self.base_url}")
                    self.print_info("Ejecuta: npm run dev")
                    self.tests_failed += 1
                    return False
                except Exception as e:
                    self.print_error(f"Error: {str(e)}")
                    self.tests_failed += 1
                    return False
    
            # ==========================================
            # TEST 2: Listar Productos
            # ==========================================
            def test_productos(self):
                self.print_header("TEST 2: GET /api/productos")
                try:
                    response = requests.get(f"{self.base_url}/api/productos", timeout=TIMEOUT)
            
                    if response.status_code == 200:
                        data = response.json()
                        total = data.get('total', 0)
                        categorias = data.get('categorias', [])
                        productos = data.get('productos', [])
                
                        self.print_success(f"Lista de productos obtenida")
                        self.print_info(f"Total productos: {total}")
                        self.print_info(f"Categorías: {', '.join(categorias[:4])}...")
                
                        if productos:
                            self.print_info(f"Ejemplo producto: {productos[0].get('nombre', 'N/A')}")
                
                        if total >= 40:  # Esperamos al menos 40 productos
                            self.tests_passed += 1
                        else:
                            self.print_error(f"Pocos productos: {total} (esperado >= 40)")
                            self.tests_failed += 1
                    else:
                        self.print_error(f"Error: {response.status_code}")
                        self.tests_failed += 1
                
                except Exception as e:
                    self.print_error(f"Error: {str(e)}")
                    self.tests_failed += 1
    
            # ==========================================
            # TEST 3: Identificación de Producto
            # ==========================================
            def test_identificar_producto(self):
                self.print_header("TEST 3: POST /api/identificar-producto")
                try:
                    # Crear imagen de prueba
                    image_buffer = self.create_test_image()
                    files = {'image': ('test.jpg', image_buffer, 'image/jpeg')}
            
                    self.print_info("Enviando imagen de prueba...")
                    response = requests.post(
                        f"{self.base_url}/api/identificar-producto",
                        files=files,
                        timeout=TIMEOUT
                    )
            
                    if response.status_code == 200:
                        data = response.json()
                
                        if data.get('success'):
                            producto = data.get('producto', {})
                            prediccion = data.get('prediccion_ventas', {})
                            relacionados = data.get('productos_relacionados', [])
                    
                            self.print_success("Producto identificado correctamente")
                            self.print_info(f"Producto: {producto.get('nombre', 'N/A')}")
                            self.print_info(f"Categoría: {producto.get('categoria', 'N/A')}")
                            self.print_info(f"Precio: ${producto.get('precio', 0)}")
                            self.print_info(f"Confianza: {producto.get('confianza', 0)*100:.1f}%")
                    
                            # Verificar predicción de ventas
                            if prediccion and 'proximos_7_dias' in prediccion:
                                self.print_info(f"Predicción 7 días: {prediccion['proximos_7_dias']}")
                                self.print_info(f"Tendencia: {prediccion.get('tendencia', 'N/A')}")
                    
                            # Verificar productos relacionados
                            if relacionados:
                                self.print_info(f"Productos relacionados: {len(relacionados)}")
                                if relacionados:
                                    self.print_info(f"  - {relacionados[0].get('nombre', 'N/A')}")
                    
                            # Validaciones
                            checks = [
                                ('producto' in data, "Tiene campo 'producto'"),
                                ('prediccion_ventas' in data, "Tiene predicción de ventas"),
                                ('productos_relacionados' in data, "Tiene productos relacionados"),
                                (producto.get('confianza', 0) > 0, "Confianza > 0"),
                                (len(relacionados) > 0, "Tiene productos relacionados"),
                            ]
                    
                            all_passed = all(check[0] for check in checks)
                    
                            for passed, desc in checks:
                                if passed:
                                    self.print_success(desc)
                                else:
                                    self.print_error(desc)
                    
                            if all_passed:
                                self.tests_passed += 1
                            else:
                                self.tests_failed += 1
                        else:
                            self.print_error(f"Identificación falló: {data.get('mensaje', 'N/A')}")
                            self.tests_failed += 1
                    else:
                        self.print_error(f"Error HTTP: {response.status_code}")
                        self.tests_failed += 1
                
                except Exception as e:
                    self.print_error(f"Error: {str(e)}")
                    self.tests_failed += 1
    
            # ==========================================
            # TEST 4: Endpoint Raíz
            # ==========================================
            def test_root_endpoint(self):
                self.print_header("TEST 4: GET /")
                try:
                    response = requests.get(f"{self.base_url}/", timeout=TIMEOUT)
            
                    if response.status_code == 200:
                        data = response.json()
                        self.print_success("Endpoint raíz respondió correctamente")
                        self.print_info(f"Servicio: {data.get('nombre', 'N/A')}")
                        self.print_info(f"Productos: {data.get('productos', 0)}")
                        self.tests_passed += 1
                    else:
                        self.print_error(f"Error: {response.status_code}")
                        self.tests_failed += 1
                
                except Exception as e:
                    self.print_error(f"Error: {str(e)}")
                    self.tests_failed += 1
    
            # ==========================================
            # TEST 5: Validación de Errores
            # ==========================================
            def test_error_handling(self):
                self.print_header("TEST 5: MANEJO DE ERRORES")
                try:
                    # Test sin imagen
                    self.print_info("Probando request sin imagen...")
                    response = requests.post(
                        f"{self.base_url}/api/identificar-producto",
                        timeout=TIMEOUT
                    )
            
                    if response.status_code == 400:
                        self.print_success("Responde 400 cuando no hay imagen")
                        data = response.json()
                        if not data.get('success'):
                            self.print_success("Campo 'success' es false")
                            self.tests_passed += 1
                        else:
                            self.print_error("Campo 'success' debería ser false")
                            self.tests_failed += 1
                    else:
                        self.print_error(f"Esperaba 400, recibió {response.status_code}")
                        self.tests_failed += 1
                
                except Exception as e:
                    self.print_error(f"Error: {str(e)}")
                    self.tests_failed += 1
    
            # ==========================================
            # Ejecutar todos los tests
            # ==========================================
            def run_all_tests(self):
                """Ejecuta todos los tests"""
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}")
                print("╔════════════════════════════════════════════════════════════════════╗")
                print("║          TEST COMPLETO - DL SERVICE API                            ║")
                print("║          Microservicio de Deep Learning                            ║")
                print("╚════════════════════════════════════════════════════════════════════╝")
                print(Style.RESET_ALL)
        
                start_time = time.time()
        
                # Ejecutar tests en orden
                if not self.test_health():
                    self.print_error("Servicio no disponible. Abortando tests.")
                    return
        
                self.test_productos()
                self.test_identificar_producto()
                self.test_root_endpoint()
                self.test_error_handling()
        
                # Resumen final
                elapsed = time.time() - start_time
                self.print_header("RESUMEN DE TESTS")
        
                total = self.tests_passed + self.tests_failed
                print(f"{Fore.WHITE}Tests ejecutados: {total}")
                print(f"{Fore.GREEN}Tests exitosos:   {self.tests_passed}")
                print(f"{Fore.RED}Tests fallidos:   {self.tests_failed}")
                print(f"{Fore.CYAN}Tiempo total:     {elapsed:.2f}s\n")
        
                if self.tests_failed == 0:
                    print(f"{Fore.GREEN}{Style.BRIGHT}")
                    print("╔════════════════════════════════════════════════════════════════════╗")
                    print("║                    ✅ TODOS LOS TESTS PASARON ✅                   ║")
                    print("╚════════════════════════════════════════════════════════════════════╝")
                    print(Style.RESET_ALL)
                    return 0
                else:
                    print(f"{Fore.RED}{Style.BRIGHT}")
                    print("╔════════════════════════════════════════════════════════════════════╗")
                    print(f"║            ❌ {self.tests_failed} TEST(S) FALLARON ❌                          ║")
                    print("╚════════════════════════════════════════════════════════════════════╝")
                    print(Style.RESET_ALL)
                    return 1


        def main():
            """Función principal"""
            tester = TestDLService()
            exit_code = tester.run_all_tests()
            sys.exit(exit_code)


        if __name__ == "__main__":
            main()
