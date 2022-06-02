#include<Wire.h>

unsigned long pir_time = 0;
int pir = 2, r = 9, g = 8, b = 7;
int pins[] = {3, 4, 5, 6};
char states_string[] = {'0', '0', '0', '0', '0', '0'};

void setup() {
  // put your setup code here, to run once:

  Wire.begin(8);
  Wire.onReceive(reader);
  Wire.onRequest(request);
  Serial.begin(115200);
  pinMode(pir,INPUT);
  pinMode(r, OUTPUT);
  pinMode(g, OUTPUT);
  pinMode(b, OUTPUT);
  pinMode(pins[0], OUTPUT);
  pinMode(pins[1], OUTPUT);
  pinMode(pins[2], OUTPUT);
  pinMode(pins[3], OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  if (digitalRead(pir)) {
    pir_time = micros();
  }
}

bool compare(char arr[]) {
  for (int i = 0; i < 4; i++) {
    if (states_string[i] != arr[i])
      return true;
  }

  return false;
}

void reader(int howMany) {
  Serial.print("Data Read as = ");
  char input[] = {'0', '0', '0', '0', '0', '0', '0', '0'};
  
  for (int i = 0; i < howMany; i++) {
    char c = Wire.read();
    input[i] = c;
    Serial.print(c);
  }
  
  Serial.print("\n");

  if (input[0] > '1') {
    // RGB Connections
    Serial.print("RGB Value = ");
    Serial.print(input[1]);
    Serial.print(input[2]);
    Serial.print(input[3]);
    Serial.print("\n");
    digitalWrite(r, input[1] - '0');
    digitalWrite(g, input[2] - '0');
    digitalWrite(b, input[3] - '0');
  } else {
    // compare states
    if (compare(input)) {
      if (states_string[1] == '0' && input[1] == '1') {
        pir_time = micros();
      }
      
      for (int i = 0; i < 4; i++) {
        states_string[i] = input[i];
        
        if (input[i] == '1') {
          digitalWrite(pins[i], 1);
        } else {
          digitalWrite(pins[i], 0);
        }
      }
    }
    
    int water_sensor = 0, ten = 1;

    for (int i = 7; i >= 4; i--) {
      water_sensor += ten * (input[i] - '0');
      ten *= 10;
    }

    Serial.print("Water Sensor Value = ");
    Serial.println(water_sensor);

    if (input[1] == '1' && water_sensor > 1700) {
      states_string[1] = '0';
      digitalWrite(pins[1], 0);
      states_string[4] = '1';
    }

    unsigned long now_time = micros();

    if (input[2] == '1' && ((now_time - pir_time) / 1000000) > 10) {
      states_string[2] = '0';
      digitalWrite(pins[2], 0);
      states_string[5] = '1';
    }
  }
}

void request() {
  for (int i = 0; i < sizeof(states_string); i++) {
    Serial.print(states_string[i]);
  }
  Serial.print("\n");
  
  Wire.write(states_string);
  states_string[4] = '0';
  states_string[5] = '0';
}
