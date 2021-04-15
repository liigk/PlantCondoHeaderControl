
#include <DHT.h>
#include <Servo.h>

int read_soil_humid();
void get_temp_and_humid(float *, float *, float*);
void move_motor_XY(int x, int y);
void oppen_gipeer();
void close_gripper();

static const int servoPin = 5;
Servo servo1;
static const int servoPin2 = 6;
Servo servo2;

#define DHTTYPE DHT11   // DHT 11 
const int moist = A4;
const int dht_pin = A5;

const int light_pin = A6;
const int max_light = 1023;
const int min_light = 397;
int raw_light = 0;


const int air_val = 864;
const int water_val = 386;


//soil moisture level
int moist_read = 0;

//ambiant temperature and humidity
float temp;
float humid;
float intent;
DHT dht(dht_pin, DHTTYPE);

String instruction = "";
String sub_instruc = "";
bool not_read = true;

//RGB

//

// the setup function runs once when you press reset or power the board
void setup() {
  
  // initialize digital pin LED_BUILTIN as an output.
  Serial.begin(9600);
  dht.begin();
  servo1.attach(servoPin);
  servo1.write (0);
  servo2.attach(servoPin2);
  servo2.write(97);
 
}

// the loop function runs over and over again forever
void loop() {

  while(!Serial.available() ){
  }
  instruction = Serial.readString();
  instruction.trim();
  delay(100);

  if (instruction == "soil"){
    servo2.write(0);
    while(!Serial.available() ){
    }
    sub_instruc = Serial.readString();
    moist_read = read_soil_humid();
    Serial.println(moist_read);
    while(!Serial.available() ){
    }
    sub_instruc = Serial.readString();
    servo2.write(97);
  }
  else if (instruction == "temphumid"){
    //get instruction on movement
    get_temp_and_humid(&humid, &temp, &intent);
    Serial.print(humid);
    Serial.print(",");
    Serial.print(temp);
    Serial.print(",");
    Serial.println(intent);
  }
  else if (instruction == "grip_close"){
    close_gripper();
  }
  else if(instruction == "grip_open"){
    oppen_gipeer();
  }
  else if(instruction == "down_soil"){
      servo2.write(0);
  }
  else if(instruction == "up_soil"){
      servo2.write(97);
  }
  else{
    Serial.println("instruction given is not correct");
  }

}

int read_soil_humid (){
  //TODO: move motor to right position
  //TODO: move motor down

  delay(100);
  moist_read = analogRead(moist);
  moist_read = map(moist_read, air_val, water_val, 0, 100);
  if(moist_read < 0){
    moist_read = 0;
  }

  delay(100);
  return moist_read;
  
  //TODO: move motor up

}
void get_temp_and_humid(float *humid, float *temp, float *intent){
  *humid = dht.readHumidity();
  // Read temperature as Celsius
  *temp = dht.readTemperature();
  raw_light = analogRead(light_pin);
  *intent = map(raw_light, min_light, max_light, 0, 100);
}

void close_gripper(){
  servo1.write(0);
}

void oppen_gipeer(){
    for(int posDegrees = 0  ; posDegrees <= 22; posDegrees++) {
      servo1.write(posDegrees);
      delay(10);
  }
}
