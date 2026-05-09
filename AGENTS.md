# AGENTS.md

## Idioma

**Regla obligatoria:** Todo el proyecto es en español exclusivamente.
- Documentación, comentarios, commits, mensajes y strings UI → español
- Excepción: identificadores y código (nombres de variables, funciones, clases) pueden ir en inglés por convención técnica

## Descripción del proyecto

Control de acceso para puerta con Arduino Uno y lector MFRC522. Lee UIDs de tarjetas, activa un relay si hay coincidencia y envía datos seriales estructurados (`ACCESO:UUID:Nombre` / `DENEGADO:UUID`) a una interfaz Python que registra los accesos en MySQL.

## Comandos

- **Compilar:** `pio run`
- **Subir al Arduino:** `pio run --target upload`
- **Monitor serial:** `pio device monitor`
- **Limpiar:** `pio run --target clean`
- **Instalar dependencias:** `pio pkg install` (se ejecuta automáticamente al compilar)
- **Ejecutar interfaz Python:** `python interfaz.py` (normal) o `python interfaz.py --test` (datos simulados, sin Arduino)
- **Iniciar base de datos:** `docker compose -f mysql-adminer.yml up -d`
- **Detener base de datos:** `docker compose -f mysql-adminer.yml down`

## Arquitectura

- **Punto de entrada:** `src/rfid_code.cpp`
- **Interfaz Python:** `interfaz.py` — GUI Tkinter + registro MySQL + ventana de consulta
- **Simulador de pruebas:** `test_simulator.py` — generación modular de datos de prueba y poblado de DB
- **Configuración:** `platformio.ini` — entorno `uno`, plataforma atmelavr, framework Arduino
- **Dependencia:** `miguelbalboa/MFRC522@^1.4.12` (gestionado por PlatformIO, almacenado en `.pio/`)
- **`archivos/`** — código de referencia/legado, no forma parte del build

## Pines de hardware

| Pin | Función |
|-----|---------|
| 9   | MFRC522 RST |
| 10  | MFRC522 SS (SPI) |
| 8   | Relay (lógica inversa: HIGH=apagado, LOW=encendido) |

## Protocolo serial (Arduino → Python)

- `READY\n` — enviado al iniciar
- `ACCESO:XXXXXXXX:Nombre\n` — acceso concedido (UID en hex, sin espacios)
- `DENEGADO:XXXXXXXX\n` — acceso denegado
- `CERRADO\n` — relay cerrado tras el delay

## Esquema MySQL

Tabla `accesos` en la base `rfid_registro` (creada por `mysql-adminer.yml`):

```sql
CREATE TABLE accesos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(20) NOT NULL,
    nombre VARCHAR(100),
    acceso_concedido BOOLEAN NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Detalles importantes

- Array de usuarios en `src/rfid_code.cpp` — agregar/quitar entradas en la struct `usuarios[]` para cambiar acceso
- Relay usa lógica inversa: `HIGH` = apagado (por defecto), `LOW` = encendido (puerta abierta)
- La interfaz Python lee de `/dev/ttyUSB0` a 9600 baud; cambiar constante `PUERTO` si el puerto difiere
- El flag `--test` inicia un hilo simulador que genera eventos aleatorios cada 3 segundos
- `test_simulator.py` — modular: `generar_linea()`, `poblar_db_prueba()`, `start_simulator(callback)`. Agregar nuevos usuarios de prueba en `USUARIOS_TEST`
- Python usa estilo funcional (globales + funciones), no clases
- Las consultas de la ventana de consulta corren en hilo secundario; el treeview se actualiza vía `after()` — la ventana principal nunca se bloquea
- El botón "Poblar DB" (solo en modo test) inserta ~22 registros con marcas de tiempo variadas (última hora, hoy, semana pasada) para probar todos los rangos de consulta
- Las credenciales de la DB están hardcodeadas en las constantes de `interfaz.py`: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Docker compose (`mysql-adminer.yml`) crea la base `rfid_registro` automáticamente; la tabla `accesos` debe crearse manualmente
- No hay tests unitarios; `test/` es el placeholder por defecto de PlatformIO
