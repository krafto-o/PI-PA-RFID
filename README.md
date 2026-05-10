# Control de Acceso RFID

Sistema de control de acceso para puerta con Arduino Uno y lector MFRC522. Lee UIDs de tarjetas MIFARE, activa un relay si hay coincidencia y envía datos seriales estructurados a una interfaz Python que registra los accesos en MySQL.

## Estructura del Repositorio

```
├── src/                    # Código fuente Arduino
│   └── rfid_code.cpp       # Firmware principal
├── interfaz.py             # Interfaz Python con modo test (--test)
├── interfaz_v2.py          # Interfaz con tema Equilux y modo test
├── interfaz_final.py       # Versión final estándar (sin test)
├── interfaz_v2_final.py    # Versión final con tema Equilux (sin test)
├── test_simulator.py       # Módulo de simulación para pruebas
├── mysql-adminer.yml       # Docker Compose: MySQL + Adminer
├── platformio.ini          # Configuración PlatformIO
├── flujo_sistema.md        # Flujo detallado del sistema
├── pseudocodigo.md         # Pseudocódigo (estilo libre + PSeInt)
├── Esquema_BD.md           # Esquema de la base de datos
├── materiales.md           # Lista de materiales necesarios
├── bibliografia.md         # Referencias y documentación externa
├── arduino.pdf             # Diagrama de conexión Arduino
├── interfaz.pdf            # Diagrama de flujo de la interfaz
└── Diagrama_conexion_arduino.pdf  # Esquema de cableado
```

## Hardware

### Materiales

Ver [`materiales.md`](materiales.md) para la lista completa.

| Componente | Modelo |
|------------|--------|
| Microcontrolador | Arduino Uno |
| Lector RFID | MFRC522 (RC522) |
| Relay | HL-52S (2 canales) |
| Tarjetas | MIFARE Classic 1K |

### Pines

| Pin | Función |
|-----|---------|
| 9 | MFRC522 RST |
| 10 | MFRC522 SS (SPI) |
| 8 | Relay (lógica inversa: HIGH=apagado, LOW=encendido) |

## Código Arduino

### Archivo principal

[`src/rfid_code.cpp`](src/rfid_code.cpp)

### Dependencias

- **Framework:** Arduino (atmelavr)
- **Librería:** [`miguelbalboa/MFRC522@^1.4.12`](https://github.com/miguelbalboa/rfid)
- **Built-in:** SPI

### Configuración

Ver [`platformio.ini`](platformio.ini)

### Comandos

```bash
pio run                    # Compilar
pio run --target upload    # Subir al Arduino
pio device monitor         # Monitor serial
pio run --target clean     # Limpiar build
```

## Interfaz Python

### Versiones disponibles

| Archivo | Tema | Modo test | Descripción |
|---------|------|-----------|-------------|
| `interfaz_final.py` | Estándar (tk) | No | Versión de producción, sin dependencias extras |
| `interfaz_v2_final.py` | Equilux (ttkthemes) | No | Versión de producción con tema oscuro y colores de acento |
| `interfaz.py` | Estándar (tk) | Sí | Incluye simulador para pruebas sin hardware |
| `interfaz_v2.py` | Equilux (ttkthemes) | Sí | Tema oscuro + simulador |

### Dependencias Python

| Paquete | Versión mínima | Uso |
|---------|---------------|-----|
| `pyserial` | >=3.5 | Comunicación serial con Arduino |
| `mysql-connector-python` | >=8.0 | Conexión a MySQL |
| `ttkthemes` | >=4.2.0 | Temas para ttk (solo v2) |

### Instalación

```bash
pip install pyserial mysql-connector-python
pip install ttkthemes  # Solo para versiones v2
```

### Ejecución

```bash
python interfaz_final.py              # Producción estándar
python interfaz_v2_final.py           # Producción con tema Equilux
python interfaz.py --test             # Modo test con simulador
python interfaz_v2.py --test          # Modo test con tema Equilux
```

### Simulador de pruebas

[`test_simulator.py`](test_simulator.py) — Módulo modular con:

- `generar_linea()` — Genera línea de protocolo serial aleatoria
- `parsear_linea()` — Parsea línea a diccionario
- `insertar_registro()` — Inserta registro con fecha arbitraria
- `poblar_db_prueba()` — Inserta ~22 registros con fechas variadas
- `start_simulator(callback)` — Thread que genera eventos cada 3s

## Base de Datos

### Esquema

Ver [`Esquema_BD.md`](Esquema_BD.md)

```sql
CREATE TABLE accesos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),
    acceso_concedido BOOLEAN NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Docker (MySQL + Adminer)

Ver [`mysql-adminer.yml`](mysql-adminer.yml)

```bash
docker compose -f mysql-adminer.yml up -d   # Iniciar
docker compose -f mysql-adminer.yml down    # Detener
```

Adminer disponible en `http://localhost:8080`:

- **System:** MySQL
- **Server:** `mysql-db`
- **Username:** `root`
- **Password:** `root`
- **Database:** `rfid_registro`

## Protocolo Serial

| Mensaje | Dirección | Significado |
|---------|-----------|-------------|
| `READY\n` | Arduino → Python | Sistema inicializado |
| `ACCESO:XXXXXXXX:Nombre\n` | Arduino → Python | Acceso concedido |
| `DENEGADO:XXXXXXXX\n` | Arduino → Python | Acceso denegado |
| `CERRADO\n` | Arduino → Python | Relay desactivado |

## Documentación

| Archivo | Contenido |
|---------|-----------|
| [`flujo_sistema.md`](flujo_sistema.md) | Flujo detallado del sistema con diagramas ASCII |
| [`pseudocodigo.md`](pseudocodigo.md) | Pseudocódigo en estilo libre y PSeInt |
| [`bibliografia.md`](bibliografia.md) | Referencias externas y documentación de librerías |
| [`materiales.md`](materiales.md) | Lista de materiales necesarios |
| [`Esquema_BD.md`](Esquema_BD.md) | Esquema de la tabla `accesos` |
| `arduino.pdf` | Diagrama de conexión del Arduino |
| `interfaz.pdf` | Diagrama de flujo de la interfaz Python |
| `Diagrama_conexion_arduino.pdf` | Esquema de cableado |
