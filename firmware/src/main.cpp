#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_MLX90614.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <math.h>
#include "pins.h"

// Firmware publishes JSONL on UART. A null means no current valid reading.
// Sensors are optional and failed discovery must not fabricate zero measurements.
Adafruit_MPU6050 imu;
Adafruit_MLX90614 irTemp;
OneWire oneWire(EDGE_ONEWIRE_PIN);
DallasTemperature contactTemp(&oneWire);
bool imuOk = false;
bool irOk = false;
bool contactOk = false;
bool contactPending = false;
float lastContactC = NAN;
uint32_t contactStartedMs = 0;
uint32_t lastContactRequestMs = 0;
uint32_t lastContactReadMs = 0;
bool contactFresh = false;
uint32_t lastEmitMs = 0;
uint32_t seq = 0;
char sessionId[32];

static void printNumberOrNull(float value, int places = 3) {
  if (isfinite(value)) Serial.print(value, places);
  else Serial.print("null");
}

static void requestContactTemperature(uint32_t now) {
  if (!contactOk || contactPending || now - lastContactRequestMs < 1000) return;
  contactTemp.requestTemperatures();  // asynchronous, setWaitForConversion(false)
  contactStartedMs = now;
  lastContactRequestMs = now;
  contactPending = true;
}

static void pollContactTemperature(uint32_t now) {
  if (!contactPending || now - contactStartedMs < 750) return; // max 12-bit conversion time
  float t = contactTemp.getTempCByIndex(0);
  lastContactC = (t == DEVICE_DISCONNECTED_C || t < -55 || t > 125) ? NAN : t;
  contactPending = false;
  if (isfinite(lastContactC)) { lastContactReadMs = now; contactFresh = true; }
}

void setup() {
  Serial.begin(EDGE_SERIAL_BAUD);
  delay(600);
  Wire.begin(EDGE_I2C_SDA, EDGE_I2C_SCL);
  Wire.setClock(100000);
  imuOk = imu.begin(0x68, &Wire);
  if (imuOk) {
    imu.setAccelerometerRange(MPU6050_RANGE_4_G);
    imu.setGyroRange(MPU6050_RANGE_500_DEG);
    imu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }
  irOk = irTemp.begin(0x5A, &Wire);
  contactTemp.begin();
  contactOk = contactTemp.getDeviceCount() > 0;
  contactTemp.setResolution(12);
  contactTemp.setWaitForConversion(false);
  snprintf(sessionId, sizeof(sessionId), "boot-%08lx", (unsigned long)esp_random());
  Serial.printf("{\"kind\":\"boot\",\"schema\":1,\"session\":\"%s\",\"imu_ready\":%s,\"ir_ready\":%s,\"contact_ready\":%s}\n",
    sessionId, imuOk ? "true" : "false", irOk ? "true" : "false", contactOk ? "true" : "false");
}

void loop() {
  uint32_t now = millis();
  pollContactTemperature(now);
  requestContactTemperature(now);
  if (now - lastEmitMs < 50) return;  // target 20 output frames/s, not a guaranteed sensor rate
  lastEmitMs = now;
  float ax=NAN, ay=NAN, az=NAN, gx=NAN, gy=NAN, gz=NAN;
  if (imuOk) {
    sensors_event_t accel, gyro, temp;
    if (imu.getEvent(&accel, &gyro, &temp)) {
      ax = accel.acceleration.x; ay = accel.acceleration.y; az = accel.acceleration.z;
      gx = gyro.gyro.x; gy = gyro.gyro.y; gz = gyro.gyro.z;
    }
  }
  // Poll IR at 20Hz for simplicity; MLX90614 response can be slower.
  float objectC = irOk ? irTemp.readObjectTempC() : NAN;
  float ambientC = irOk ? irTemp.readAmbientTempC() : NAN;
  if (objectC < -70 || objectC > 380) objectC = NAN;
  if (ambientC < -40 || ambientC > 125) ambientC = NAN;

  Serial.printf("{\"kind\":\"sample\",\"schema\":1,\"mode\":\"environment\",\"session\":\"%s\",\"seq\":%lu,\"uptime_ms\":%lu,\"imu\":{\"ax_mps2\":", sessionId,(unsigned long)seq++,(unsigned long)now);
  printNumberOrNull(ax); Serial.print(",\"ay_mps2\":"); printNumberOrNull(ay);
  Serial.print(",\"az_mps2\":"); printNumberOrNull(az);
  Serial.print(",\"gx_rads\":"); printNumberOrNull(gx);
  Serial.print(",\"gy_rads\":"); printNumberOrNull(gy);
  Serial.print(",\"gz_rads\":"); printNumberOrNull(gz);
  Serial.print("},\"thermal\":{\"object_c\":"); printNumberOrNull(objectC);
  Serial.print(",\"ambient_c\":"); printNumberOrNull(ambientC);
  Serial.print(",\"contact_c\":"); printNumberOrNull(lastContactC);
  Serial.printf(",\"contact_new\":%s,\"contact_age_ms\":", contactFresh ? "true" : "false");
  if (isfinite(lastContactC)) Serial.print((unsigned long)(now-lastContactReadMs));
  else Serial.print("null");
  Serial.println("}}");
  contactFresh = false;
}
