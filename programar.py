"""
Programador: deja este script corriendo en una terminal o como servicio.
Ejecuta el reporte automáticamente cada lunes a la hora configurada.

Para producción real conviene usar el Programador de Tareas de Windows
o cron en Linux apuntando a 'main.py'.
"""

import schedule
import time
from datetime import datetime
import sys

from main import ejecutar

try:
    import config
except ImportError:
    print("ERROR: no existe 'config.py'. Copia 'config.example.py' primero.")
    sys.exit(1)


def trabajo():
    print("\n" + "=" * 60)
    print(f"  TRIGGER PROGRAMADO  ·  {datetime.now()}")
    print("=" * 60)
    ejecutar()


# Programar según config
dia = config.DIA_ENVIO.lower()
hora = config.HORA_ENVIO

dias_validos = ['monday', 'tuesday', 'wednesday', 'thursday',
                'friday', 'saturday', 'sunday']
if dia not in dias_validos:
    print(f"ERROR: DIA_ENVIO debe ser uno de {dias_validos}")
    sys.exit(1)

getattr(schedule.every(), dia).at(hora).do(trabajo)

print("=" * 60)
print("  PROGRAMADOR ACTIVO")
print("=" * 60)
print(f"  Tarea: enviar reporte cada {dia.upper()} a las {hora}")
print(f"  Destinatarios: {', '.join(config.DESTINATARIOS)}")
print(f"  Proxima ejecucion: {schedule.next_run()}")
print("  (Ctrl+C para detener)")
print("=" * 60)

while True:
    schedule.run_pending()
    time.sleep(30)
