from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.services import AlertEvaluator
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Verifica todas las reglas de alertas activas y dispara las que correspondan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando verificación de alertas - {start_time}')
        )
        
        try:
            triggered_count = AlertEvaluator.check_all_active_rules()
            
            end_time = timezone.now()
            duration = end_time - start_time
            
            if options['verbose']:
                self.stdout.write(f'Tiempo de ejecución: {duration.total_seconds():.2f} segundos')
                self.stdout.write(f'Alertas disparadas: {triggered_count}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Verificación completada. {triggered_count} alertas disparadas.'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante la verificación: {str(e)}')
            )
            logger.error(f'Error en check_alerts: {str(e)}')
            raise