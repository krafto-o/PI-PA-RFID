#include <Arduino.h>
#include <MFRC522.h>
#include <SPI.h>

#define RST_PIN 9
#define SS_PIN 10

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  while (!Serial)
    ; // Espera a que abra el monitor serie

  SPI.begin();
  mfrc522.PCD_Init();

  Serial.println("Prueba de comunicación SPI iniciada.");
  Serial.print("Versión del firmware del lector: ");

  // Esta línea intenta leer directamente la memoria del chip
  mfrc522.PCD_DumpVersionToSerial();
}

void loop() {
  // No necesitamos nada en el loop para esta prueba
}
