#include <Wire.h>
#include <MFRC522.h>
#include <SPI.h>

#define SS_PIN 10
#define RST_PIN 9

int nfcIsPresent;

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  // put your setup code here, to run once:
  Wire.begin(4);
  Serial.begin(9600);
  Wire.onRequest(requestEvent);
  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {
  // put your main code here, to run repeatedly:
   if ( ! mfrc522.PICC_IsNewCardPresent()) {
    nfcIsPresent = 0;
    return;
  }
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    nfcIsPresent = 0;
    return;
  }
  nfcIsPresent = 0;
  nfcIsPresent = nfcIsPresent + mfrc522.uid.size;
  Serial.println(nfcIsPresent);

}

void requestEvent() {
  if (nfcIsPresent > 0){
    Wire.write(1);
  }
  if (nfcIsPresent == 0 ) {
    Wire.write(0);
  }
}

