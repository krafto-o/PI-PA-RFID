#include <Arduino.h>
#include <MFRC522.h>
#include <SPI.h>

#define RST_PIN 9
#define SS_PIN 10
#define RELAY_PIN 8
#define TIEMPO_RELAY 5000

MFRC522 mfrc522(SS_PIN, RST_PIN);

struct Usuario {
  byte uid[4];
  const char *nombre;
};

Usuario usuarios[] = {
    {{0xC3, 0xE4, 0x5F, 0x95}, "Usuario1"},
    {{0xCA, 0x3F, 0x1C, 0x06}, "Usuario2"},
    {{0x53, 0xE9, 0x30, 0x06}, "Usuario3"},
};
const byte NUM_USUARIOS = sizeof(usuarios) / sizeof(usuarios[0]);

void printUID(byte *uid, byte size) {
  for (byte i = 0; i < size; i++) {
    if (uid[i] < 0x10)
      Serial.print("0");
    Serial.print(uid[i], HEX);
  }
}

int buscarUsuario(byte *uidLeido) {
  for (byte u = 0; u < NUM_USUARIOS; u++) {
    bool coincide = true;
    for (byte i = 0; i < 4; i++) {
      if (uidLeido[i] != usuarios[u].uid[i]) {
        coincide = false;
        break;
      }
    }
    if (coincide)
      return u;
  }
  return -1;
}

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);

  Serial.println("READY");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  int idx = buscarUsuario(mfrc522.uid.uidByte);

  if (idx >= 0) {
    Serial.print("ACCESO:");
    printUID(mfrc522.uid.uidByte, mfrc522.uid.size);
    Serial.print(":");
    Serial.println(usuarios[idx].nombre);

    digitalWrite(RELAY_PIN, LOW);
    delay(TIEMPO_RELAY);
    digitalWrite(RELAY_PIN, HIGH);

    Serial.println("CERRADO");
  } else {
    Serial.print("DENEGADO:");
    printUID(mfrc522.uid.uidByte, mfrc522.uid.size);
    Serial.println();
  }

  mfrc522.PICC_HaltA();
}
