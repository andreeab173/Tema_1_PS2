#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 8
#define internalPIN 13

OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

void setup(void)
{
  Serial.begin(9600);
  sensors.begin();
  pinMode(internalPIN, OUTPUT);
  digitalWrite(internalPIN,LOW);

}

void loop(void){ 
  sensors.requestTemperatures(); 
  
  Serial.print("Celsius temperature: ");
  Serial.print(sensors.getTempCByIndex(0));
  Serial.print("\n"); 

  if(Serial.available() > 0)
  {
    char caracter = Serial.read();
    if(caracter == 'A')
      digitalWrite(internalPIN,HIGH);
    else if (caracter == 'S')
      digitalWrite(internalPIN,LOW);
    else
      Serial.print("Tasta gresita!\n");

  }

  delay(1000);
}