#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <MAX30105.h> // SparkFun library exposes MAX30102 through MAX30105 class
#include <math.h>
#include "pins.h"

Adafruit_MPU6050 imu;
MAX30105 optical;
bool imuOk=false, ppgOk=false;
char sessionId[32];
uint32_t seq=0, lastEmitMs=0;
static void printNum(float n) {if (isfinite(n)) Serial.print(n, 3); else Serial.print("null");}

void setup() {
  Serial.begin(EDGE_SERIAL_BAUD);
  delay(600);
  Wire.begin(EDGE_I2C_SDA, EDGE_I2C_SCL);
  Wire.setClock(400000);
  imuOk = imu.begin(0x68, &Wire);
  if (imuOk) {imu.setAccelerometerRange(MPU6050_RANGE_4_G); imu.setGyroRange(MPU6050_RANGE_500_DEG);}
  ppgOk = optical.begin(Wire, I2C_SPEED_FAST);
  if (ppgOk) {
    // Safe low-current prototype setup, NOT validated for oxygen saturation or heart rate.
    optical.setup(0x0A, 4, 2, 100, 411, 4096);
    optical.setPulseAmplitudeGreen(0);
  }
  snprintf(sessionId, sizeof(sessionId), "boot-%08lx", (unsigned long)esp_random());
  Serial.printf("{\"kind\":\"boot\",\"schema\":1,\"session\":\"%s\",\"imu_ready\":%s,\"ppg_ready\":%s}\n", sessionId, imuOk?"true":"false",ppgOk?"true":"false");
}

void loop() {
  uint32_t now=millis();
  if(now-lastEmitMs<20) return; // 50 frames/s; optical FIFO can hold more than one frame
  lastEmitMs=now;
  float ax=NAN,ay=NAN,az=NAN, gx=NAN,gy=NAN,gz=NAN;
  if(imuOk){sensors_event_t a,g,t; if(imu.getEvent(&a,&g,&t)){
    ax=a.acceleration.x;ay=a.acceleration.y;az=a.acceleration.z;
    gx=g.gyro.x;gy=g.gyro.y;gz=g.gyro.z;
  }}
  bool gotPpg=false;
  uint32_t red=0,ir=0;
  if (ppgOk) {
    optical.check(); // transfer available FIFO data
    if (optical.available()) {
      red=optical.getRed(); ir=optical.getIR(); gotPpg=true;
      optical.nextSample(); // FIFO may contain more; capture gaps are assessed on host
    }
  }
  Serial.printf("{\"kind\":\"sample\",\"schema\":1,\"mode\":\"ppg_motion\",\"session\":\"%s\",\"seq\":%lu,\"uptime_ms\":%lu,\"imu\":{\"ax_mps2\":",sessionId,(unsigned long)seq++,(unsigned long)now);
  printNum(ax);Serial.print(",\"ay_mps2\":");printNum(ay);
  Serial.print(",\"az_mps2\":");printNum(az);
  Serial.print(",\"gx_rads\":");printNum(gx);
  Serial.print(",\"gy_rads\":");printNum(gy);
  Serial.print(",\"gz_rads\":");printNum(gz);
  Serial.print("},\"ppg\":{\"red\":"); if(gotPpg) Serial.print(red); else Serial.print("null");
  Serial.print(",\"ir\":"); if(gotPpg) Serial.print(ir); else Serial.print("null");
  Serial.println("}}");
}
