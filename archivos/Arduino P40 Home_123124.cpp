/*

  Code Author: CHULE41
  PEEK TECHNOLOGIES

*/

#include <SPI.h>			    // Incluye libreria bus SPI
#include <MFRC522.h>			// Incluye libreria especifica para MFRC522
#define RST_PIN  9			  // Constante para referenciar pin de reset
#define SS_PIN  10			  // Constante para referenciar pin de slave select

MFRC522 mfrc522(SS_PIN, RST_PIN);	// Crea objeto mfrc522 enviando pines de slave select y reset

byte LecturaUID[4]; 				// Crea array para almacenar el UID leido
byte TJulian[4]= {0xC0, 0x86, 0xC6, 0x22} ;    // UID de tarjeta Julian
byte TErik[4]= {0xB3, 0x88, 0x7A, 0x95} ;      // UID de tarjeta Erik
byte TMama[4]= {0x63, 0xCA, 0x40, 0x95} ;      // UID de tarjeta Mama
byte LlaveroSOS[4]= {0x12, 0x37, 0xD7, 0x1B} ;    // UID de llavero de emergencia

int Buzz = 8;  // Pin para activar el buzzer activo
int Rele = 7;  // Pin para activar el relevador

void setup() {

  Serial.begin(9600);			// Inicializa comunicacion por monitor serie a 9600 bps
  
  SPI.begin();				// Inicializa bus SPI

  mfrc522.PCD_Init();			// Inicializa modulo lector
  
  pinMode(Buzz, OUTPUT);  // Declarando la salida del pin
  pinMode(Rele, OUTPUT);  // Declarando la salida del pin

  Serial.println("Listo");		// Muestra texto Listo
  Serial.println("UID = Identificador Unico De RFID");    // Muestra texto def UID  

}

void loop() {
  
  if ( ! mfrc522.PICC_IsNewCardPresent())		// Si no hay una tarjeta presente

    return;						// Retorna al loop esperando por una tarjeta
  
  if ( ! mfrc522.PICC_ReadCardSerial()) 		// Si no puede obtener datos de la tarjeta
  
    return;						// Retorna al loop esperando por otra tarjeta
    
    Serial.print("UID:");				// Muestra texto UID:
    
    for (byte i = 0; i < mfrc522.uid.size; i++) {	// Bucle recorre de a un byte por vez el UID
    
      if (mfrc522.uid.uidByte[i] < 0x10){		// Si el byte leido es menor a 0x10

        Serial.print(" 0");				// Imprime espacio en blanco y numero cero
        
        }
        
        else{						// Si no

          Serial.print(" ");				// Imprime un espacio en blanco

          }
          
          Serial.print(mfrc522.uid.uidByte[i], HEX);   	// Imprime el byte del UID leido en hexadecimal
          
          LecturaUID[i]=mfrc522.uid.uidByte[i];   	// Almacena en array el byte del UID leido      
          
          }
          
          Serial.print("\t");   			// Imprime un espacio de tabulacion             
                    
          if(comparaUID(LecturaUID, TJulian)){		// Llama a funcion comparaUID con TJulian
          
            Serial.println("Bienvenido Julian");	// Si retorna verdadero muestra texto bienvenida
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Rele, HIGH);       // Activador del relevador
            delay(500);         // TImer por medio segundo
            digitalWrite(Rele, LOW);        // Desactivador del relevador            
            
          }
          
          else if(comparaUID(LecturaUID, TErik)){	// Llama a funcion comparaUID con TErik
          
            Serial.println("Bienvenido Erik");	// Si retorna verdadero muestra texto bienvenida
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Rele, HIGH);       // Activador del relevador
            delay(500);         // TImer por medio segundo
            digitalWrite(Rele, LOW);        // Desactivador del relevador  
            
          }                      
          
          else if(comparaUID(LecturaUID, TMama)){	// Llama a funcion comparaUID con TMama
          
            Serial.println("Bienvenido Mama");	// Si retorna verdadero muestra texto bienvenida
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Rele, HIGH);       // Activador del relevador
            delay(500);         // TImer por medio segundo
            digitalWrite(Rele, LOW);        // Desactivador del relevador              

          }

          else if(comparaUID(LecturaUID, LlaveroSOS)){	// Llama a funcion comparaUID con LlaveroSOS
          
            Serial.println("Bienvenido Usuario Llavero");	// Si retorna verdadero muestra texto bienvenida
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Buzz, HIGH);       // Activador de buzzer
            delay(50);        // Timer por 50 ms
            digitalWrite(Buzz, LOW);        // Desactivador de buzzer
            delay(100);       // Timer por 100 ms
            digitalWrite(Rele, HIGH);       // Activador del relevador
            delay(500);         // TImer por medio segundo
            digitalWrite(Rele, LOW);        // Desactivador del relevador  
            
          } 

          else						// Si retorna falso
          
            Serial.println("UID Desconocido"); 		// Muestra texto equivalente a acceso denegado          
                  
                  mfrc522.PICC_HaltA();  		// Detiene comunicacion con tarjeta                
                  
}

boolean comparaUID(byte lectura[],byte usuario[])	// Funcion comparaUID

{
  
  for (byte i=0; i < mfrc522.uid.size; i++){		// Bucle recorre de a un byte por vez el UID
  
  if(lectura[i] != usuario[i])				// Si byte de UID leido es distinto a usuario
  
    return(false);					// Retorna falso
    
  }
  
  return(true);						// Si los 4 bytes coinciden retorna verdadero

}