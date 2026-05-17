# Reporte Automático de Ventas

Sistema en Python que lee un archivo Excel de ventas, genera un reporte semanal en **PDF profesional** y lo envía por **correo electrónico** a una lista de destinatarios. Pensado para correr automáticamente cada lunes a primera hora.

## Problema que resuelve

El dueño de un negocio quiere recibir cada lunes el resumen de la semana pasada sin tener que abrir Excel, hacer fórmulas o pedírselo al contador. Este script automatiza el proceso completo: extrae los datos, calcula los KPIs, los compara contra la semana anterior, dibuja las gráficas, arma el PDF y lo manda por correo. Una vez configurado, no se vuelve a tocar.

## Características

- **Reporte PDF** con diseño editorial (paleta oscura, tipografía profesional)
- **Indicadores principales**: ventas totales, transacciones, ticket promedio, unidades
- **Comparativa automática** contra la semana anterior (variación porcentual)
- **Gráfica diaria** de ventas por día de la semana
- **Top 10 productos** con unidades e ingreso
- **Distribución por categoría** en gráfica de barras
- **Envío SMTP** compatible con Gmail, Outlook, Yahoo y servidores estándar
- **Programación semanal** integrada — corre solo cada lunes
- **Configuración separada** del código en `config.py` (no se sube al repo)

## Tecnologías

- Python 3.10+
- Pandas + openpyxl (lectura de Excel)
- ReportLab (generación de PDF)
- Matplotlib (gráficas embebidas)
- smtplib (envío de correo, librería estándar)
- schedule (programación semanal)

## Instalación

```bash
git clone https://github.com/israel44moran/reporte-automatico-ventas.git
cd reporte-automatico-ventas
pip install -r requirements.txt
```

## Configuración

1. Copia el archivo de plantilla a tu configuración real:

   ```bash
   copy config.example.py config.py
   ```

2. Edita `config.py` con tus datos:

   - **Para Gmail** debes activar la verificación en 2 pasos y crear una *contraseña de aplicación* de 16 caracteres en `https://myaccount.google.com/apppasswords`. Esa es la que va en `SMTP_PASSWORD`.
   - **Para Outlook**: usa `smtp-mail.outlook.com` puerto `587` con tu contraseña normal.

3. Genera datos de demostración (opcional):

   ```bash
   python generar_datos.py
   ```

## Uso

### Generar y enviar el reporte una sola vez

```bash
python main.py
```

### Probar solo el PDF (sin enviar correo)

```bash
python reporte.py
```

Esto crea `reporte_semanal.pdf` en la carpeta actual.

### Dejarlo corriendo en automático

```bash
python programar.py
```

El script queda corriendo y dispara el reporte el día y hora que pusiste en `config.py` (por defecto: lunes 08:00).

### Programar como tarea de Windows (recomendado para producción)

En vez de dejar `programar.py` corriendo, abre el **Programador de tareas** y crea una tarea que ejecute:

```
python C:\ruta\a\reporte-automatico-ventas\main.py
```

Configurada para correrse semanalmente los lunes a las 08:00. Esto es más confiable porque sobrevive a reinicios.

## Estructura del proyecto

```
reporte-automatico-ventas/
├── main.py                 # Orquestador (genera + envia)
├── reporte.py              # Generacion del PDF
├── enviar.py               # Envio SMTP del correo
├── programar.py            # Loop semanal con schedule
├── generar_datos.py        # Datos de demostracion
├── config.example.py       # Plantilla de configuracion
├── config.py               # Tu config real (NO subir al repo)
├── ventas.xlsx             # Datos de ventas
├── requirements.txt
├── .gitignore
└── README.md
```

## Formato esperado del Excel

| Columna | Descripción | Requerida |
|---------|-------------|-----------|
| `fecha` | Fecha y hora de la venta | Sí |
| `producto` | Nombre del producto | Sí |
| `total` | Importe de la venta | Sí (o `precio_unitario` + `cantidad`) |
| `cantidad` | Unidades vendidas | Opcional |
| `precio_unitario` | Precio por unidad | Opcional |
| `categoria` | Categoría del producto | Opcional |
| `id_venta` | Folio único de venta | Opcional |
| `metodo_pago` | Forma de pago | Opcional |

## Extensión a WhatsApp

Para enviar el mismo PDF por WhatsApp se puede integrar la API de **Twilio** o **WhatsApp Business**. Ambas requieren cuenta verificada y tienen costo por mensaje. La estructura de `enviar.py` está pensada para añadir un módulo paralelo `enviar_whatsapp.py` que reutilice el PDF generado.

## Autor

Israel Moran
