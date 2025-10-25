#!/usr/bin/env python3
"""
Test completo del Microservicio ML
Prueba todos los endpoints y funcionalidades del ML Service

Uso:
    python3 tests/test_ml_service.py
    
Requisitos:
    - core-service corriendo en puerto 8080
    - ml-service corriendo en puerto 8081
    - Datos poblados en core-service
"""

import requests
import json
import time
from typing import Dict, Any, List
from datetime import datetime


class Colors:
    """Colores para output en terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class MLServiceTester:
    """Clase para probar el microservicio ML"""
    
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.core_service_url = "http://localhost:8080"
        self.tests_passed = 0
        self.tests_failed = 0
        self.start_time = None
        
    def print_header(self, text: str):
        """Imprime encabezado de sección"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        
    def print_test(self, name: str, status: bool, details: str = ""):
        """Imprime resultado de test"""
        if status:
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} {name}")
            if details:
                print(f"  {Colors.OKCYAN}{details}{Colors.ENDC}")
            self.tests_passed += 1
        else:
            print(f"{Colors.FAIL}✗{Colors.ENDC} {name}")
            if details:
                print(f"  {Colors.FAIL}{details}{Colors.ENDC}")
            self.tests_failed += 1
            
    def print_info(self, text: str):
        """Imprime información"""
        print(f"{Colors.OKBLUE}ℹ{Colors.ENDC} {text}")
        
    def print_warning(self, text: str):
        """Imprime advertencia"""
        print(f"{Colors.WARNING}⚠{Colors.ENDC} {text}")
        
    def test_core_service_connectivity(self) -> bool:
        """Verifica conectividad con core-service"""
        self.print_header("1. VERIFICACIÓN DE CORE SERVICE")
        
        try:
            # Test GraphQL endpoint
            query = '{"query": "{__typename}"}'
            response = requests.post(
                f"{self.core_service_url}/graphql",
                data=query,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                self.print_test(
                    "Conectividad con core-service",
                    True,
                    f"GraphQL endpoint respondiendo en puerto 8080"
                )
                return True
            else:
                self.print_test(
                    "Conectividad con core-service",
                    False,
                    f"Status code: {response.status_code}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_test(
                "Conectividad con core-service",
                False,
                f"Error: {str(e)}"
            )
            self.print_warning("Asegúrate de que core-service esté corriendo en puerto 8080")
            return False
            
    def test_ml_service_health(self) -> bool:
        """Verifica health check del ML service"""
        self.print_header("2. HEALTH CHECK ML SERVICE")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.print_test(
                    "Health endpoint",
                    True,
                    f"Status: {data.get('status', 'unknown')}"
                )
                
                # Verificar detalles
                if data.get('core_service_reachable'):
                    self.print_test("Core service alcanzable", True)
                else:
                    self.print_test("Core service alcanzable", False)
                    
                return True
            else:
                self.print_test(
                    "Health endpoint",
                    False,
                    f"Status code: {response.status_code}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_test(
                "Health endpoint",
                False,
                f"Error: {str(e)}"
            )
            self.print_warning("Asegúrate de que ml-service esté corriendo en puerto 8081")
            return False
            
    def test_data_sync(self) -> Dict[str, Any]:
        """Prueba sincronización de datos"""
        self.print_header("3. SINCRONIZACIÓN DE DATOS")
        
        try:
            self.print_info("Iniciando sincronización (puede tardar 5-10 segundos)...")
            start = time.time()
            
            response = requests.post(f"{self.base_url}/sync", timeout=30)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_test(
                    "Sincronización exitosa",
                    True,
                    f"Completada en {elapsed:.2f} segundos"
                )
                
                # Verificar datos sincronizados
                productos = data.get('productos_synced', 0)
                ventas = data.get('ventas_synced', 0)
                clientes = data.get('clientes_synced', 0)
                
                self.print_test(
                    f"Productos sincronizados: {productos}",
                    productos > 0,
                    f"Se esperaban al menos 10 productos"
                )
                
                self.print_test(
                    f"Ventas sincronizadas: {ventas}",
                    ventas > 0,
                    f"Se esperaban al menos 50 ventas"
                )
                
                self.print_test(
                    f"Clientes sincronizados: {clientes}",
                    clientes > 0,
                    f"Se esperaban al menos 10 clientes"
                )
                
                return data
            else:
                self.print_test(
                    "Sincronización",
                    False,
                    f"Status code: {response.status_code}"
                )
                return {}
                
        except requests.exceptions.RequestException as e:
            self.print_test(
                "Sincronización",
                False,
                f"Error: {str(e)}"
            )
            return {}
            
    def test_price_prediction(self):
        """Prueba predicción de precios (ML Supervisado)"""
        self.print_header("4. PREDICCIÓN DE PRECIOS (ML SUPERVISADO)")
        
        # Casos de prueba
        test_cases = [
            {
                "nombre": "Producto Bebidas",
                "data": {
                    "categoria": "Bebidas",
                    "stock": 50,
                    "nombre": "Jugo Natural de Naranja 1L"
                }
            },
            {
                "nombre": "Producto Lácteos",
                "data": {
                    "categoria": "Lácteos",
                    "stock": 100,
                    "nombre": "Yogurt Griego"
                }
            },
            {
                "nombre": "Producto Limpieza",
                "data": {
                    "categoria": "Limpieza",
                    "stock": 30,
                    "nombre": "Detergente Líquido 2L"
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/predict/price",
                    json=test_case["data"],
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    precio = result.get('precio_sugerido', 0)
                    
                    # Validar que el precio tenga sentido
                    precio_valido = 0.5 <= precio <= 100
                    
                    self.print_test(
                        test_case["nombre"],
                        precio_valido,
                        f"Precio sugerido: ${precio:.2f}"
                    )
                else:
                    self.print_test(
                        test_case["nombre"],
                        False,
                        f"Status code: {response.status_code}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.print_test(
                    test_case["nombre"],
                    False,
                    f"Error: {str(e)}"
                )
                
    def test_customer_segmentation(self):
        """Prueba segmentación de clientes (ML No Supervisado)"""
        self.print_header("5. SEGMENTACIÓN DE CLIENTES (ML NO SUPERVISADO)")
        
        try:
            response = requests.get(f"{self.base_url}/ml/segmentacion", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                total_clientes = data.get('total_clientes', 0)
                vip_count = data.get('vip_count', 0)
                regular_count = data.get('regular_count', 0)
                ocasional_count = data.get('ocasional_count', 0)
                clientes = data.get('clientes', [])
                
                self.print_test(
                    "Segmentación ejecutada",
                    total_clientes > 0,
                    f"Total clientes: {total_clientes}"
                )
                
                # Verificar que hay clientes en cada segmento
                self.print_info(f"Distribución de segmentos:")
                self.print_info(f"  VIP: {vip_count} clientes")
                self.print_info(f"  Regular: {regular_count} clientes")
                self.print_info(f"  Ocasional: {ocasional_count} clientes")
                
                # Verificar que la suma cuadra
                suma_correcta = (vip_count + regular_count + ocasional_count) == total_clientes
                self.print_test(
                    "Suma de segmentos correcta",
                    suma_correcta,
                    f"{vip_count} + {regular_count} + {ocasional_count} = {total_clientes}"
                )
                
                # Mostrar ejemplos de cada segmento
                if clientes:
                    for segmento in ['VIP', 'Regular', 'Ocasional']:
                        ejemplos = [c for c in clientes if c.get('segmento') == segmento][:2]
                        if ejemplos:
                            self.print_info(f"\nEjemplos de clientes {segmento}:")
                            for cliente in ejemplos:
                                self.print_info(
                                    f"  - {cliente.get('nombre')}: "
                                    f"${cliente.get('total_compras', 0):.2f} en "
                                    f"{cliente.get('frecuencia', 0)} compras"
                                )
                                
            else:
                self.print_test(
                    "Segmentación",
                    False,
                    f"Status code: {response.status_code}"
                )
                
        except requests.exceptions.RequestException as e:
            self.print_test(
                "Segmentación",
                False,
                f"Error: {str(e)}"
            )
            
    def test_anomaly_detection(self):
        """Prueba detección de anomalías (ML Semi-Supervisado)"""
        self.print_header("6. DETECCIÓN DE ANOMALÍAS (ML SEMI-SUPERVISADO)")
        
        try:
            response = requests.get(f"{self.base_url}/ml/anomalias", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                total_ventas = data.get('total_ventas_analizadas', 0)
                anomalias_count = data.get('anomalias_detectadas', 0)
                anomalias = data.get('anomalias', [])
                
                self.print_test(
                    "Detección ejecutada",
                    total_ventas > 0,
                    f"Ventas analizadas: {total_ventas}"
                )
                
                # Verificar que se detectaron anomalías
                porcentaje = (anomalias_count / total_ventas * 100) if total_ventas > 0 else 0
                
                self.print_test(
                    "Anomalías detectadas",
                    anomalias_count > 0,
                    f"{anomalias_count} anomalías ({porcentaje:.1f}% del total)"
                )
                
                # Validar que el porcentaje de anomalías es razonable (5-15%)
                porcentaje_razonable = 5 <= porcentaje <= 20
                self.print_test(
                    "Porcentaje de anomalías razonable",
                    porcentaje_razonable,
                    f"{porcentaje:.1f}% está dentro del rango esperado (5-20%)"
                )
                
                # Mostrar ejemplos de anomalías
                if anomalias:
                    self.print_info(f"\nEjemplos de anomalías detectadas:")
                    for i, anomalia in enumerate(anomalias[:3], 1):
                        self.print_info(
                            f"  {i}. Venta #{anomalia.get('venta_id')}: "
                            f"${anomalia.get('total', 0):.2f} - "
                            f"{anomalia.get('razon', 'Sin razón')}"
                        )
                        
            else:
                self.print_test(
                    "Detección de anomalías",
                    False,
                    f"Status code: {response.status_code}"
                )
                
        except requests.exceptions.RequestException as e:
            self.print_test(
                "Detección de anomalías",
                False,
                f"Error: {str(e)}"
            )
            
    def test_models_metadata(self):
        """Prueba endpoint de metadata de modelos"""
        self.print_header("7. METADATA DE MODELOS")
        
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                self.print_test(
                    "Endpoint de modelos",
                    len(models) > 0,
                    f"{len(models)} modelos registrados"
                )
                
                # Verificar que están los 3 modelos esperados
                expected_models = ['price_predictor', 'customer_segmentation', 'anomaly_detector']
                
                for model_name in expected_models:
                    model_found = any(m.get('model_name') == model_name for m in models)
                    self.print_test(
                        f"Modelo '{model_name}' registrado",
                        model_found
                    )
                    
                # Mostrar info de cada modelo
                if models:
                    self.print_info("\nDetalle de modelos:")
                    for model in models:
                        self.print_info(
                            f"  - {model.get('model_name')}: "
                            f"{model.get('samples_count', 0)} muestras, "
                            f"entrenado: {model.get('trained_at', 'N/A')}"
                        )
                        
            else:
                self.print_test(
                    "Metadata de modelos",
                    False,
                    f"Status code: {response.status_code}"
                )
                
        except requests.exceptions.RequestException as e:
            self.print_test(
                "Metadata de modelos",
                False,
                f"Error: {str(e)}"
            )
            
    def test_root_endpoint(self):
        """Prueba endpoint raíz"""
        self.print_header("8. ENDPOINT RAÍZ (INFO)")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                self.print_test(
                    "Endpoint raíz",
                    True,
                    f"Servicio: {data.get('service', 'N/A')}"
                )
                
                # Mostrar info disponible
                self.print_info("Información del servicio:")
                for key, value in data.items():
                    if isinstance(value, dict):
                        self.print_info(f"  {key}:")
                        for k, v in value.items():
                            self.print_info(f"    - {k}: {v}")
                    else:
                        self.print_info(f"  {key}: {value}")
                        
            else:
                self.print_test(
                    "Endpoint raíz",
                    False,
                    f"Status code: {response.status_code}"
                )
                
        except requests.exceptions.RequestException as e:
            self.print_test(
                "Endpoint raíz",
                False,
                f"Error: {str(e)}"
            )
            
    def print_summary(self):
        """Imprime resumen final"""
        self.print_header("RESUMEN DE TESTS")
        
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        print(f"{Colors.BOLD}Tests ejecutados:{Colors.ENDC} {total_tests}")
        print(f"{Colors.OKGREEN}Tests exitosos:{Colors.ENDC} {self.tests_passed}")
        
        if self.tests_failed > 0:
            print(f"{Colors.FAIL}Tests fallidos:{Colors.ENDC} {self.tests_failed}")
        else:
            print(f"{Colors.OKGREEN}Tests fallidos:{Colors.ENDC} 0")
            
        print(f"{Colors.BOLD}Tasa de éxito:{Colors.ENDC} {success_rate:.1f}%")
        print(f"{Colors.BOLD}Tiempo total:{Colors.ENDC} {elapsed:.2f} segundos")
        
        print()
        if self.tests_failed == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ TODOS LOS TESTS PASARON ✓{Colors.ENDC}")
            print(f"{Colors.OKGREEN}El microservicio ML está funcionando correctamente{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}✗ ALGUNOS TESTS FALLARON ✗{Colors.ENDC}")
            print(f"{Colors.WARNING}Revisa los errores anteriores{Colors.ENDC}")
            
        print()
        
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        self.start_time = time.time()
        
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║                                                                   ║")
        print("║           TEST COMPLETO DEL MICROSERVICIO ML                      ║")
        print("║                                                                   ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        self.print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.print_info(f"ML Service URL: {self.base_url}")
        self.print_info(f"Core Service URL: {self.core_service_url}")
        
        # Ejecutar tests en orden
        if not self.test_core_service_connectivity():
            self.print_warning("Core service no disponible. Algunos tests pueden fallar.")
            
        if not self.test_ml_service_health():
            self.print_warning("ML service no disponible. Abortando tests.")
            self.print_summary()
            return
            
        # Sincronizar datos (crítico para los demás tests)
        sync_result = self.test_data_sync()
        if not sync_result:
            self.print_warning("Sincronización falló. Tests de ML pueden fallar.")
            
        # Tests de ML
        self.test_price_prediction()
        self.test_customer_segmentation()
        self.test_anomaly_detection()
        
        # Tests adicionales
        self.test_models_metadata()
        self.test_root_endpoint()
        
        # Resumen final
        self.print_summary()


def main():
    """Función principal"""
    tester = MLServiceTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
