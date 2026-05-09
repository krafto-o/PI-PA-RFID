#include <Arduino.h>
#include <MFRC522.h>
#include <SPI.h>

// Definición de pines
#define RST_PIN 9
#define SS_PIN 10
#define RELAY_PIN 8

// Instancia del lector RFID
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Define aquí el UID de tu tarjeta autorizada
// Necesitarás leer tu tarjeta una vez para conocer estos valores y
// reemplazarlos
byte tarjetaAutorizada[4] = {0xC3, 0xE4, 0x5F, 0x95};

void setup() {
  Serial.begin(9600); // Inicializa comunicación serie para debugging
  SPI.begin();        // Inicializa el bus SPI
  mfrc522.PCD_Init(); // Inicializa el módulo MFRC522

  // Configuración del relevador
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Comienza apagado (Lógica inversa)

  Serial.println("Sistema inicializado. Acerca tu tarjeta al lector...");
}

void loop() {
  // 1. Revisa si hay una tarjeta nueva presente
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return; // Si no hay tarjeta, reinicia el loop
  }

  Serial.print("UID leído: ");
  bool accesoConcedido = true;

  // 2. Compara el UID leído con el UID autorizado
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522.uid.uidByte[i], HEX);

    if (mfrc522.uid.uidByte[i] != tarjetaAutorizada[i]) {
      accesoConcedido = false;
    }
  }
  Serial.println();

  // 3. Ejecuta la acción del relevador
  if (accesoConcedido) {
    Serial.println("Acceso concedido. Abriendo...");
    digitalWrite(RELAY_PIN, HIGH); // Activa el relevador
    delay(5000);                   // Mantiene abierto por 3 segundos
    digitalWrite(RELAY_PIN, LOW);  // Desactiva el relevador
    Serial.println("Cerrado.");
  } else {
    Serial.println("Acceso denegado.");
  }

  // 4. Detiene la lectura de la tarjeta actual para evitar lecturas repetidas
  // instantáneas
  mfrc522.PICC_HaltA();
}
