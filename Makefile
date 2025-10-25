# ================================================
# Makefile - Proyecto SW2
# Comandos comunes para gestión rápida del sistema
# ================================================

.PHONY: help up down build rebuild start stop restart logs status clean init populate reset health test

# Variables
COMPOSE = docker-compose
SCRIPTS = ./scripts

# Color output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

##@ Ayuda

help: ## Mostrar esta ayuda
	@echo ""
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║           COMANDOS DISPONIBLES - PROYECTO SW2           ║$(NC)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Desarrollo Rápido

start: ## Levantar todos los servicios
	@echo "$(GREEN)🚀 Iniciando servicios...$(NC)"
	@$(COMPOSE) up -d
	@echo "$(GREEN)✅ Servicios iniciados$(NC)"
	@make status

stop: ## Detener todos los servicios
	@echo "$(YELLOW)⏸️  Deteniendo servicios...$(NC)"
	@$(COMPOSE) stop
	@echo "$(GREEN)✅ Servicios detenidos$(NC)"

restart: ## Reiniciar todos los servicios
	@echo "$(BLUE)🔄 Reiniciando servicios...$(NC)"
	@$(COMPOSE) restart
	@echo "$(GREEN)✅ Servicios reiniciados$(NC)"

down: ## Detener y eliminar contenedores
	@echo "$(RED)🛑 Deteniendo y eliminando contenedores...$(NC)"
	@$(COMPOSE) down
	@echo "$(GREEN)✅ Contenedores eliminados$(NC)"

##@ Build & Deploy

build: ## Construir imágenes Docker
	@echo "$(BLUE)🔨 Construyendo imágenes...$(NC)"
	@$(COMPOSE) build
	@echo "$(GREEN)✅ Imágenes construidas$(NC)"

rebuild: down build start ## Rebuild completo (down + build + start)
	@echo "$(GREEN)✅ Rebuild completo finalizado$(NC)"

up: build start ## Build + Start
	@echo "$(GREEN)✅ Sistema levantado$(NC)"

##@ Datos

init: ## Inicialización completa (servicios + datos + ML/DL)
	@echo "$(BLUE)🎯 Inicialización completa del sistema...$(NC)"
	@make start
	@sleep 5
	@cd $(SCRIPTS) && ./inicializacion_completa.sh

populate: ## Solo poblar datos (sin limpiar)
	@echo "$(BLUE)📝 Poblando base de datos...$(NC)"
	@cd $(SCRIPTS) && python3 generar_datos_ml_realistas.py
	@echo "$(GREEN)✅ Datos poblados$(NC)"

clean: ## Limpiar base de datos
	@echo "$(RED)🧹 Limpiando base de datos...$(NC)"
	@cd $(SCRIPTS) && ./limpiar_datos.sh
	@echo "$(GREEN)✅ Base de datos limpiada$(NC)"

reset: clean populate ## Limpiar y poblar (reset completo de datos)
	@echo "$(GREEN)✅ Reset de datos completado$(NC)"

##@ Monitoreo

status: ## Ver estado de servicios
	@echo ""
	@echo "$(BLUE)📊 Estado de servicios:$(NC)"
	@$(COMPOSE) ps

logs: ## Ver logs en tiempo real (Ctrl+C para salir)
	@$(COMPOSE) logs -f

logs-core: ## Ver logs del Core Service
	@$(COMPOSE) logs -f core-service

logs-ml: ## Ver logs del ML Service
	@$(COMPOSE) logs -f ml-service

logs-dl: ## Ver logs del DL Service
	@$(COMPOSE) logs -f dl-service

logs-frontend: ## Ver logs del Frontend
	@$(COMPOSE) logs -f frontend

health: ## Verificar health checks
	@echo ""
	@echo "$(BLUE)🏥 Health Checks:$(NC)"
	@echo ""
	@echo -n "  Core Service:    "
	@curl -sf http://localhost:8080/actuator/health > /dev/null 2>&1 && echo "$(GREEN)✓ OK$(NC)" || echo "$(RED)✗ FAIL$(NC)"
	@echo -n "  ML Service:      "
	@curl -sf http://localhost:8081/health > /dev/null 2>&1 && echo "$(GREEN)✓ OK$(NC)" || echo "$(RED)✗ FAIL$(NC)"
	@echo -n "  DL Service:      "
	@curl -sf http://localhost:8082/health > /dev/null 2>&1 && echo "$(GREEN)✓ OK$(NC)" || echo "$(RED)✗ FAIL$(NC)"
	@echo -n "  Frontend:        "
	@curl -sf http://localhost:5173 > /dev/null 2>&1 && echo "$(GREEN)✓ OK$(NC)" || echo "$(RED)✗ FAIL$(NC)"
	@echo ""

##@ Limpieza Profunda

clean-volumes: ## Eliminar volúmenes (DESTRUCTIVO - borra datos)
	@echo "$(RED)⚠️  ADVERTENCIA: Esto eliminará TODOS los datos persistentes$(NC)"
	@read -p "¿Continuar? (escriba 'SI'): " confirm; \
	if [ "$$confirm" = "SI" ]; then \
		$(COMPOSE) down -v; \
		echo "$(GREEN)✅ Volúmenes eliminados$(NC)"; \
	else \
		echo "$(YELLOW)❌ Operación cancelada$(NC)"; \
	fi

clean-all: ## Limpieza total (contenedores + volúmenes + imágenes)
	@echo "$(RED)⚠️  ADVERTENCIA: Limpieza TOTAL del sistema$(NC)"
	@read -p "¿Continuar? (escriba 'SI'): " confirm; \
	if [ "$$confirm" = "SI" ]; then \
		$(COMPOSE) down -v --rmi local; \
		docker system prune -f; \
		echo "$(GREEN)✅ Limpieza total completada$(NC)"; \
	else \
		echo "$(YELLOW)❌ Operación cancelada$(NC)"; \
	fi

##@ Testing

test: ## Ejecutar todos los tests
	@echo "$(BLUE)🧪 Ejecutando tests...$(NC)"
	@echo ""
	@echo "$(YELLOW)Core Service:$(NC)"
	@cd core-service && ./mvnw test || true
	@echo ""
	@echo "$(YELLOW)ML Service:$(NC)"
	@cd ml-service/tests && pytest test_ml_service.py -v || true
	@echo ""
	@echo "$(YELLOW)DL Service:$(NC)"
	@cd dl-service/tests && python3 test_api_completo.py || true

##@ URLs

urls: ## Mostrar URLs de acceso
	@echo ""
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║                    URLs DE ACCESO                       ║$(NC)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  $(GREEN)Frontend:$(NC)        http://localhost:5173"
	@echo "  $(GREEN)Core API:$(NC)        http://localhost:8080/graphiql"
	@echo "  $(GREEN)ML API:$(NC)          http://localhost:8081/docs"
	@echo "  $(GREEN)DL API:$(NC)          http://localhost:8082"
	@echo "  $(GREEN)H2 Console:$(NC)      http://localhost:8080/h2-console"
	@echo ""

##@ Desarrollo

shell-core: ## Shell en Core Service
	@$(COMPOSE) exec core-service sh

shell-ml: ## Shell en ML Service
	@$(COMPOSE) exec ml-service sh

shell-dl: ## Shell en DL Service
	@$(COMPOSE) exec dl-service sh

shell-frontend: ## Shell en Frontend
	@$(COMPOSE) exec frontend sh

##@ Atajos Populares

dev: up init urls ## Todo desde cero (build + start + init + URLs)
	@echo ""
	@echo "$(GREEN)╔══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║              ✅ SISTEMA LISTO PARA DESARROLLO            ║$(NC)"
	@echo "$(GREEN)╚══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""

quick: start urls ## Inicio rápido (solo start + URLs)
	@echo ""
	@echo "$(GREEN)✅ Sistema iniciado$(NC)"
	@echo ""

# Default target
.DEFAULT_GOAL := help
