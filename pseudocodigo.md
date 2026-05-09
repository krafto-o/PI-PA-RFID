# Pseudocódigo - Control de Acceso RFID

## 1. Versión Estilo Libre

### Arduino (`src/rfid_code.cpp`)

**Configuración Inicial**
- Iniciar comunicación serial a 9600 baudios
- Iniciar bus SPI y módulo lector MFRC522
- Configurar pin del relay como salida, establecer en ALTO (apagado)
- Enviar señal `READY` por serial

**Bucle Principal**
- Esperar tarjeta nueva
- Si no hay tarjeta presente, reiniciar bucle
- Leer UID completo de la tarjeta
- Buscar UID en el array de usuarios autorizados
- **Si coincide:**
  - Enviar `ACCESO:UID:Nombre` por serial
  - Activar relay (BAJO)
  - Esperar 5 segundos
  - Desactivar relay (ALTO)
  - Enviar `CERRADO` por serial
- **Si no coincide:**
  - Enviar `DENEGADO:UID` por serial
- Detener lectura de la tarjeta actual para evitar duplicados

---

### Python (`interfaz_v2_final.py`)

**Configuración**
- Crear ventana principal con tema visual Equilux
- Definir estilos personalizados para botones y etiquetas usando colores de acento
- Configurar parámetros de conexión serial y base de datos MySQL
- Construir interfaz gráfica: estado, UUID, log de eventos, botones de control

**Funciones Clave**
- `procesar_linea(linea)`: Recibe datos del Arduino. Si es `ACCESO`, guarda en DB y actualiza GUI. Si es `DENEGADO`, guarda y actualiza GUI.
- `insertar_acceso(uuid, nombre, estado)`: Abre conexión MySQL, ejecuta `INSERT`, cierra conexión.
- `abrir_ventana_consulta()`: Crea ventana secundaria con tabla de registros, filtros por tiempo y campo de búsqueda.
- `cargar_registros_async(rango, busqueda)`: Ejecuta consulta SQL en hilo separado para no bloquear la GUI. Al recibir datos, actualiza la tabla.
- `DataReceivedHandler()`: Hilo en segundo plano que lee continuamente del puerto serial y envía líneas a `procesar_linea`.

**Gestión de Eventos**
- **Conectar:** Abre puerto serial, inicia hilo de lectura, deshabilita botón.
- **Desconectar:** Cierra puerto serial, detiene hilo, habilita botón.
- **Salir:** Detiene hilos, cierra serial, cierra ventanas secundarias, termina aplicación.

---

## 2. Versión PSeInt

### Arduino

```pseudocode
Algoritmo Control_Acceso_RFID
    Definir uid_leido como Entero[4]
    Definir usuario_encontrado como Booleano
    
    // Configuración
    Serial.Iniciar(9600)
    SPI.Iniciar()
    MFRC522.Inicializar()
    Pin(Relay, SALIDA)
    Escribir(Relay, ALTO)
    Serial.Imprimir("READY")
    
    Mientras Verdadero Hacer
        Si MFRC522.TarjetaNueva() Y MFRC522.LeerSerial() Entonces
            uid_leido <- MFRC522.ObtenerUID()
            usuario_encontrado <- Falso
            
            Para i <- 0 Hasta 3 Con Paso 1 Hacer
                Si uid_leido[i] = Usuario_Autorizado[i] Entonces
                    usuario_encontrado <- Verdadero
                FinSi
            FinPara
            
            Si usuario_encontrado Entonces
                Serial.Imprimir("ACCESO:" + uid_leido + ":" + nombre_usuario)
                Escribir(Relay, BAJO)
                Esperar(5000)
                Escribir(Relay, ALTO)
                Serial.Imprimir("CERRADO")
            SiNo
                Serial.Imprimir("DENEGADO:" + uid_leido)
            FinSi
            
            MFRC522.DetenerLectura()
        FinSi
    FinMientras
FinAlgoritmo
```

---

### Python

```pseudocode
Proceso Interfaz_RFID
    Definir puerto_serial como Cadena
    Definir arduino_conectado como Booleano
    Definir ventana_principal, ventana_consulta como Ventana
    
    // Configuración inicial
    puerto_serial <- "/dev/ttyUSB0"
    Crear_Ventana(ventana_principal, "Control de Acceso RFID", tema="equilux")
    Configurar_Estilos_Botones()
    Configurar_Conexion_DB()
    
    // Bucle de eventos (manejado por Tkinter)
    Repetir
        Si Boton_Conectar_Presionado Entonces
            Si No arduino_conectado Entonces
                Serial.Abrir(puerto_serial, 9600)
                arduino_conectado <- Verdadero
                Crear_Hilo(Lectura_Serial)
            FinSi
        FinSi
        
        Si Boton_Consultar_Presionado Entonces
            Crear_Ventana(ventana_consulta, "Consultar Registros")
            Cargar_Registros("ultima_hora")
        FinSi
    Hasta Que Ventana_Cerrada
    
    // Subproceso Lectura_Serial
    SubProceso Lectura_Serial
        Mientras arduino_conectado Hacer
            linea <- Serial.LeerLinea()
            Si linea <> "" Entonces
                Procesar_Lineas(linea)
            FinSi
        FinMientras
    FinSubProceso
    
    // Subproceso Procesar_Lineas
    SubProceso Procesar_Lineas(linea)
        Si linea ComienzaCon "ACCESO:" Entonces
            partes <- Dividir(linea, ":")
            uuid <- partes[2]
            nombre <- partes[3]
            DB.Ejecutar("INSERT INTO accesos ...", uuid, nombre, VERDADERO)
            Actualizar_GUI(nombre, uuid, ACCESO)
        SiNo Si linea ComienzaCon "DENEGADO:" Entonces
            partes <- Dividir(linea, ":")
            uuid <- partes[2]
            DB.Ejecutar("INSERT INTO accesos ...", uuid, "Desconocido", FALSO)
            Actualizar_GUI("", uuid, DENEGADO)
        FinSi
    FinSubProceso
FinProceso
```