#include <SoftwareSerial.h>

#define EMS_OFF 0
#define EMS_INTERFERANCE 1
#define EMS_RUSSIAN  2
#define EMS_IN_OFF 0x30
#define EMS_IN_INTERFERANCE 0x31
#define EMS_IN_RUSSIAN 0x32

short curEmsType = EMS_OFF;
short newEmsType = EMS_OFF;
short ledPin = 5;
short potPin = A0;

boolean curLedState = false;
unsigned long edgeTime = 0L;

SoftwareSerial BTSerial(2, 3); // RX | TX

int getHalfPeriod() {
  int ret = 0;
  if (curEmsType == EMS_INTERFERANCE)
    ret = 500;
  else if (curEmsType == EMS_RUSSIAN)
    ret = 10000;
  return ret;
} 

void driveLed() {
  unsigned long now = millis();
  if (newEmsType != curEmsType) {
    analogWrite(ledPin, 0);
    curLedState = false;
    edgeTime = now;
    curEmsType = newEmsType;
  }

  int hPeriod = getHalfPeriod();
  if ((hPeriod > 0) && (now-edgeTime) > hPeriod) {
    if (curLedState) {
      analogWrite(ledPin, 0);
      curLedState = false;
    } else {
      analogWrite(ledPin, (255./1023.) * analogRead(potPin));
      curLedState = true;
    }
    edgeTime = now;
  } else {
    if (curLedState) {
      analogWrite(ledPin, (255./1023.) * analogRead(potPin));
    } else {
      analogWrite(ledPin, 0);
    }
  }
}

void setup() {
  pinMode(potPin, INPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  BTSerial.begin(9600);
  analogWrite(ledPin, 0);
}

short getEmsTypeFromBTinput(short dataByte) {
  short ems = EMS_OFF;
  switch (dataByte) {
      case EMS_IN_OFF:
        ems = EMS_OFF;
//        Serial.print("OFF");
        break;
      case EMS_IN_INTERFERANCE:
        ems = EMS_INTERFERANCE;
//        Serial.print("Interferance");
        break;
      case EMS_IN_RUSSIAN:
        ems = EMS_RUSSIAN;
//        Serial.print("Russian");
        break;
      default:
        // invalid BT input
        ems = EMS_OFF;
        Serial.print("failed to pars BT input");
    }
    return ems;
}

void loop() {
  if (BTSerial.available()) {   
    newEmsType = getEmsTypeFromBTinput(BTSerial.read());
  } 
  driveLed();
}
