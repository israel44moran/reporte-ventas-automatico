"""
Generador de datos de ventas para el reporte automático.
Crea un archivo Excel con 8 semanas de ventas realistas, listo para
alimentar el reporte semanal.
"""

import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

productos = [
    {"producto": "Coca-Cola 600ml",          "categoria": "Bebidas",   "precio": 22},
    {"producto": "Sabritas original",        "categoria": "Botanas",   "precio": 25},
    {"producto": "Pan Bimbo blanco",         "categoria": "Panaderia", "precio": 58},
    {"producto": "Leche Lala 1L",            "categoria": "Lacteos",   "precio": 32},
    {"producto": "Huevo 18 piezas",          "categoria": "Lacteos",   "precio": 92},
    {"producto": "Tortillas 1kg",            "categoria": "Panaderia", "precio": 25},
    {"producto": "Arroz 1kg",                "categoria": "Abarrotes", "precio": 42},
    {"producto": "Frijol 1kg",               "categoria": "Abarrotes", "precio": 52},
    {"producto": "Aceite 1L",                "categoria": "Abarrotes", "precio": 65},
    {"producto": "Azucar 1kg",               "categoria": "Abarrotes", "precio": 38},
    {"producto": "Cafe soluble",             "categoria": "Bebidas",   "precio": 78},
    {"producto": "Galletas Marias",          "categoria": "Botanas",   "precio": 22},
    {"producto": "Cerveza Corona 355ml",     "categoria": "Bebidas",   "precio": 28},
    {"producto": "Detergente 1kg",           "categoria": "Limpieza",  "precio": 72},
    {"producto": "Papel higienico 4 rollos", "categoria": "Limpieza",  "precio": 58},
    {"producto": "Jabon de bano",            "categoria": "Limpieza",  "precio": 18},
    {"producto": "Pasta dental",             "categoria": "Higiene",   "precio": 45},
    {"producto": "Shampoo 400ml",            "categoria": "Higiene",   "precio": 89},
    {"producto": "Atun en lata",             "categoria": "Abarrotes", "precio": 28},
    {"producto": "Sopa instantanea",         "categoria": "Abarrotes", "precio": 18},
]

# 8 semanas hacia atrás, terminando hoy
fecha_inicio = datetime.now() - timedelta(weeks=8)
ventas = []
id_venta = 1

for dia in range(56):
    fecha = fecha_inicio + timedelta(days=dia)

    if fecha.weekday() in [5, 6]:
        num_ventas_dia = random.randint(45, 75)
    else:
        num_ventas_dia = random.randint(25, 50)

    for _ in range(num_ventas_dia):
        hora = random.choices(
            range(7, 22),
            weights=[3, 8, 10, 7, 5, 6, 7, 5, 6, 9, 11, 10, 8, 5, 3]
        )[0]
        minuto = random.randint(0, 59)
        fecha_hora = fecha.replace(hour=hora, minute=minuto)

        productos_venta = random.sample(productos, random.randint(1, 5))
        for prod in productos_venta:
            cantidad = random.randint(1, 3)
            ventas.append({
                "id_venta": id_venta,
                "fecha": fecha_hora,
                "producto": prod["producto"],
                "categoria": prod["categoria"],
                "cantidad": cantidad,
                "precio_unitario": prod["precio"],
                "total": cantidad * prod["precio"],
                "metodo_pago": random.choices(
                    ["Efectivo", "Tarjeta", "Transferencia"],
                    weights=[60, 30, 10]
                )[0],
            })
        id_venta += 1

df = pd.DataFrame(ventas)
df.to_excel("ventas.xlsx", index=False)

print(f"[OK] Archivo 'ventas.xlsx' generado")
print(f"     - Registros: {len(df)}")
print(f"     - Periodo: {df['fecha'].min()} a {df['fecha'].max()}")
print(f"     - Total: ${df['total'].sum():,.2f}")
