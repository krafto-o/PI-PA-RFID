# Flujo del Sistema - Control de Acceso RFID

## 1. Arduino (`src/rfid_code.cpp`)

### Inicio
```
┌─────────────────────────────────┐
│  Inicializar Serial (9600 baud) │
│  Inicializar SPI                │
│  Inicializar MFRC522            │
│  Configurar Relay (ALTO=apagado)│
│  Enviar "READY" por serial      │
└──────────────┬──────────────────┘
               ▼
```

### Bucle Principal
```
┌──────────────────────────────────────┐
│  ¿Tarjeta nueva presente?            │
│  ¿Se pudo leer el serial?            │
└──────────────┬───────────────────────┘
               │
         NO ───┘ (volver al inicio del bucle)
         │
         ▼ SÍ
┌──────────────────────────────────────┐
│  Leer UID completo (4 bytes)         │
│  Buscar UID en array usuarios[]      │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
  ¿Coincide?            ¿Coincide?
    │ SÍ                  │ NO
    ▼                     ▼
┌──────────────┐    ┌──────────────────┐
│ Enviar:      │    │ Enviar:          │
│ ACCESO:      │    │ DENEGADO:UID     │
│ UID:Nombre   │    └────────┬─────────┘
└──────┬───────┘             │
       ▼                     │
┌──────────────┐             │
│ Relay BAJO   │             │
│ (encendido)  │             │
└──────┬───────┘             │
       ▼                     │
┌──────────────┐             │
│ Esperar      │             │
│ TIEMPO_RELAY │             │
│ (5000ms)     │             │
└──────┬───────┘             │
       ▼                     │
┌──────────────┐             │
│ Relay ALTO   │             │
│ (apagado)    │             │
└──────┬───────┘             │
       ▼                     │
┌──────────────┐             │
│ Enviar:      │             │
│ CERRADO      │             │
└──────┬───────┘             │
       │                     │
       └──────────┬──────────┘
                  ▼
┌──────────────────────────────────────┐
│  Detener lectura tarjeta (PICC_HaltA)│
│  Volver al inicio del bucle          │
└──────────────────────────────────────┘
```

---

## 2. Protocolo Serial

| Dirección | Mensaje | Significado |
|-----------|---------|-------------|
| Arduino → Python | `READY\n` | Sistema listo |
| Arduino → Python | `ACCESO:C3E45F95:Julian\n` | Acceso concedido |
| Arduino → Python | `DENEGADO:FF11AA22\n` | Acceso denegado |
| Arduino → Python | `CERRADO\n` | Relay desactivado |

---

## 3. Interfaz Python (`interfaz_v2_final.py`)

### Inicio
```
┌──────────────────────────────────────┐
│  Crear ventana principal (ThemedTk)  │
│  Aplicar tema Equilux                │
│  Configurar estilos de botones       │
│  Configurar estilos de labels        │
│  Construir GUI:                      │
│    - lbConexion (estado serial)      │
│    - lbEstado (acceso/denegado)      │
│    - lbUUID (UID leído)              │
│    - lbLog (último evento con hora)  │
│    - Botones: Conectar, Desconectar, │
│      Consultar, Salir                │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Iniciar mainloop()                  │
│  Esperar eventos del usuario         │
└──────────────┬───────────────────────┘
               ▼
```

### Botón "Conectar"
```
┌──────────────────────────────────────┐
│  Abrir puerto serial (/dev/ttyUSB0)  │
│  Configurar baudrate, timeout        │
│  is_connected = Verdadero            │
│  Deshabilitar botón Conectar         │
│  Habilitar botón Desconectar         │
│  lbConexion = "Conectando..."        │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Crear hilo DataReceivedHandler      │
│  (daemon=True)                       │
└──────────────┬───────────────────────┘
               ▼
```

### Hilo DataReceivedHandler (segundo plano)
```
┌──────────────────────────────────────┐
│  Mientras is_connected:              │
│    ¿Hay datos en el buffer serial?   │
└──────────────┬───────────────────────┘
               │
         NO ───┘ (continuar bucle)
         │
         ▼ SÍ
┌──────────────────────────────────────┐
│  Leer línea completa                 │
│  Decodificar UTF-8                   │
│  Llamar procesar_linea(linea)        │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  procesar_linea(linea):              │
│                                      │
│  Si "READY":                         │
│    lbConexion = "Conectado"          │
│                                      │
│  Si "ACCESO:UID:Nombre":             │
│    → insertar_acceso(uuid,nombre,T)  │
│    → ventana.after(0, actualizar_gui)│
│                                      │
│  Si "DENEGADO:UID":                  │
│    → insertar_acceso(uuid,"Descon.",F)│
│    → ventana.after(0, actualizar_gui)│
│                                      │
│  Si "CERRADO":                       │
│    → ignorar                         │
└──────────────────────────────────────┘
```

### insertar_acceso() (hilo del serial)
```
┌──────────────────────────────────────┐
│  Conectar a MySQL                    │
│  INSERT INTO accesos                 │
│    (uuid, nombre, acceso_concedido,  │
│     fecha)                           │
│  Commit                              │
│  Cerrar conexión                     │
└──────────────────────────────────────┘
```

### actualizar_gui() (hilo principal via after)
```
┌──────────────────────────────────────┐
│  ¿Hay timer_standby activo?          │
│  → Cancelarlo con after_cancel()     │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼ acceso=T            ▼ acceso=F
┌──────────────┐    ┌──────────────────┐
│ lbEstado =   │    │ lbEstado =       │
│ "ACCESO: N"  │    │ "DENEGADO"       │
│ style=Access │    │ style=Denied     │
│ lbUUID=UID   │    │ lbUUID=UID       │
└──────┬───────┘    └──────┬───────────┘
       ▼                   │
┌──────────────┐           │
│ Programar:   │           │
│ after(       │           │
│  TIEMPO_PUERTA,          │
│  volver_standby)         │
│ timer_standby=id         │
└──────┬───────┘           │
       │                   │
       └─────────┬─────────┘
                 ▼
┌──────────────────────────────────────┐
│  lbLog = "[HH:MM:SS] ACCESO/DENEGADO │
│           nombre (uuid)"             │
└──────────────────────────────────────┘
```

### volver_standby() (hilo principal via after)
```
┌──────────────────────────────────────┐
│  timer_standby = None                │
│  lbEstado = "Esperando..."           │
│  lbUUID = "UUID: ---"                │
│  (sin estilo especial)               │
└──────────────────────────────────────┘
```

---

## 4. Ventana de Consulta

### Abrir Ventana
```
┌──────────────────────────────────────┐
│  ¿Ya existe la ventana?              │
│  → Sí: traer al frente y salir       │
│  → No: crear Toplevel                │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Construir GUI:                      │
│    - 4 Radiobuttons: Hora, Día,      │
│      Semana, Mes                     │
│    - Entry búsqueda + botón Buscar   │
│    - Botón Limpiar                   │
│    - Botón Cerrar                    │
│    - Treeview (UUID, Nombre, Acceso, │
│      Fecha)                          │
│    - Label contador de registros     │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  cargar_registros_async("hora", "")  │
└──────────────┬───────────────────────┘
               ▼
```

### cargar_registros_async() (hilo secundario)
```
┌──────────────────────────────────────┐
│  lblCargando = "Cargando..."         │
│  Crear hilo de trabajo               │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  ejecutar_query(rango, busqueda):    │
│    Conectar MySQL                    │
│    Construir WHERE según rango:      │
│      hora  → fecha >= NOW()-1H       │
│      dia   → DATE(fecha)=CURDATE()   │
│      semana→ YEARWEEK=YEARWEEK       │
│      mes   → MONTH=MONTH AND YEAR    │
│    Si busqueda:                      │
│      AND (nombre LIKE %x% OR         │
│           uuid LIKE %x%)             │
│    ORDER BY fecha DESC               │
│    FETCH all                         │
│    Cerrar conexión                   │
│    Retornar filas                    │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  ventana.after(0, poblar_treeview)   │
│  (vuelve al hilo principal)          │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  poblar_treeview(rows):              │
│    Limpiar treeview                  │
│    Insertar cada fila                │
│    lblCount = "Total: N registros"   │
│    lblCargando = ""                  │
└──────────────────────────────────────┘
```

---

## 5. Cierre del Programa

### Botón "Salir" o cerrar ventana
```
┌──────────────────────────────────────┐
│  is_connected = Falso                │
│  (detiene hilo DataReceivedHandler)  │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  ¿Puerto serial abierto?             │
│  → Cerrar puerto serial              │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  ¿Ventana consulta abierta?          │
│  → Destruir ventana consulta         │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  ventana_principal.quit()            │
│  ventana_principal.destroy()         │
│  (termina aplicación)                │
└──────────────────────────────────────┘
```

---

## 6. Constantes Configurables

| Constante | Archivo | Valor | Descripción |
|-----------|---------|-------|-------------|
| `TIEMPO_RELAY` | `src/rfid_code.cpp` | `5000` | Milisegundos que el relay permanece activo |
| `TIEMPO_PUERTA` | `interfaz*.py` | `5000` | Milisegundos que la GUI muestra "ACCESO" antes de volver a standby |
| `PUERTO` | `interfaz*.py` | `/dev/ttyUSB0` | Puerto serial del Arduino |
| `BAUDIOS` | `interfaz*.py` | `9600` | Velocidad de comunicación serial |
| `usuarios[]` | `src/rfid_code.cpp` | Array | Lista de UIDs y nombres autorizados |
