#include <SoftwareSerial.h>

// defining constants for EMS types
#define EMS_OFF 0
#define EMS_INTERFERANCE 1
#define EMS_RUSSIAN  2

// defining constants for valid EMS data bytes received from HC-05
#define EMS_IN_OFF 0x30
#define EMS_IN_INTERFERANCE 0x31
#define EMS_IN_RUSSIAN 0x32

// defining global variables
short curEmsType = EMS_OFF;
short newEmsType = EMS_OFF;
short ledPin = 5; // defining LED pin
short potPin = A0; // defining Potentiometer pin
boolean curLedState = false; // current LED state
unsigned long edgeTime = 0L; // 'edge' time

// Configuring serial port to communicate with HC-05
SoftwareSerial BTSerial(2, 3); // RX | TX

/*
 * This function reports the half-period in miliseconds for current EMS type
 */
int getHalfPeriod() {
  int ret = 0;
  if (curEmsType == EMS_INTERFERANCE)
    ret = 500;
  else if (curEmsType == EMS_RUSSIAN)
    ret = 10000;
  return ret;
} 

/*
 * This fuction drives the LED based on the EMS type and the analog input obtained from potentionmeter.
 */
void driveLed() {
  unsigned long now = millis();
  if (newEmsType != curEmsType) {
    // EMS type has changed
    analogWrite(ledPin, 0);
    curLedState = false;
    edgeTime = now;
    curEmsType = newEmsType;
  }

  int hPeriod = getHalfPeriod();
  if ((hPeriod > 0) && (now-edgeTime) > hPeriod) {
    //  Elapsed time is greater than half period.
    if (curLedState) {
      // LED is currently ON, turn it OFF
      analogWrite(ledPin, 0);
      curLedState = false;
    } else {
      // LED is currently OFF, turn it ON per potentiometer input.
      analogWrite(ledPin, (255./1023.) * analogRead(potPin));
      curLedState = true;
    }
    edgeTime = now;
  } else {
    // Elapsed time is less than half period.
    if (curLedState) {
      // keep LED ON per potentiometer input
      analogWrite(ledPin, (255./1023.) * analogRead(potPin));
    } else {
      // turn LED OFF
      analogWrite(ledPin, 0);
    }
  }
}

/*
 * This is the function that is invoked by microprocessor at startup.
 * It sets up pins and initializes bloetooth serial port.
 */
void setup() {
  pinMode(potPin, INPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  BTSerial.begin(9600);
  analogWrite(ledPin, 0);
}

/*
 * This method reports EMS type for the given input obtained from HC-05 device.
 * If supplied data byte is invalid the EMS_OFF is returned.
 * 
 * @param dataByte as short
 * @returns EMS type as short
 */
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

/*
 * This is the main execution loop. This function is repeatedly called after the setup sequence is complete. 
 * The loop looks if serial information is available from the HC-05. If data is available, it reads a byte of data from HC-05 
 * using the BTSerial.read() call. The byte that was read is then passed into the getEmsTypeFromBTinput() function to be processed. 
 * After EMS type is set, the loop() invokes the driveLed() function to blink LED according to current EMS type and desired intensity obtained from 
 * 'potentiometer' input.
 */
void loop() {
  if (BTSerial.available()) {   
    newEmsType = getEmsTypeFromBTinput(BTSerial.read());
  } 
  driveLed();
}
