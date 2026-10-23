# Hardware wiring and risk controls

> **Do not assume a common ESP32-S3 pinout is authoritative for this camera PCB.** Photographs show an N16R8 module, camera connector and two USB-C ports. The code printed on the reverse (`127294G_Y1127_231016`) does not identify a confirmed circuit schematic.

## Initial bench conditions

- Unplug USB before any change in wiring, and solder pin headers before breadboard work.
- Use **one USB-UART data connection to the PC**, without battery/charger, L298N, 12 V adapter, ECG electrodes or body-connected instruments.
- Verify ground and regulator outputs with your multimeter BEFORE powering sensors.
- Never apply 5 V to ESP32-S3 GPIO. Never join unknown 5 V I²C pull-ups to a 3.3 V bus.
- Ensure both I²C breakout boards (if present together) accept **3.3 V supply and 3.3 V logic**. Chips and breakout boards can have different allowed voltages.
- Record actual measured rail values and pin checks in `experiments/EVIDENCE_LOG_TEMPLATE.md`.

## Provisional stage-1 schematic — ONLY after continuity/schematic check

```text
ESP32-S3 PCB (3.3 V only)  → GY-521 MPU6050
3V3                         → VCC [verify breakout regulator/pull-up network]
GND                         → GND
GPIO1                       → SDA
GPIO14                      → SCL

Later: GY-906 MLX90614 on same verified I²C bus; module power variant unconfirmed.
Later: DS18B20 VDD 3V3; GND GND; DQ GPIO21;
       4.7k ohm pull-up between DQ and 3V3 as appropriate for chosen probe.
```

These exact GPIO allocations match `firmware/include/pins.h` and are a **proposed laboratory profile only**. The camera and microSD are left disconnected/unused. Peripheral pin mappings may conflict when the camera/SD is installed; check the exact PCB drawing before enabling them. The ESP32-S3 has bootstrapping pins (0,3,45,46), native USB (19,20), flash/PSRAM-related GPIO and UART0 pins best left free during this phase.

## Exclusions and voltage risks

- **HY-SRF05:** many SRF05 variants use 5 V logic; do not connect the Echo pin directly to ESP32. Use a verified level shifter/divider once exact board and supply are known.
- **LCD1602 I²C backpack:** may pull SDA/SCL to 5 V. Do not connect to 3.3 V bus as-is.
- **UNO:** typical UNO GPIO is 5 V; use level adaptation for any cross-board signal.
- **ADS1115:** its PGA setting does NOT allow higher input voltage than supply rails; channels are multiplexed, not simultaneous.
- **L298N:** require a documented compatible motor and separate supply; do not use 12 V adapter with microcontroller 3.3 V pins.
- **Battery boost/charger LX-LCBST:** adjustable output and charger protection are not verified; no battery operation in the first project phase.
- **MAX30102:** main IC and module VIN are not the same. Confirm the actual breakout supply and I²C pull-ups. No clinically accurate SpO₂ output or health diagnosis.
- **AD8232:** never attach electrodes to any person while connected to a USB-powered PC/prototype. Human-connected testing needs qualified safety oversight and appropriately isolated medical-rated equipment; omitted from this firmware entirely.
- **Camera:** OV5640 is visible-light optical, not thermal. The exact ribbon pinout and camera multiplex conflicts must be verified before connection.

## Reference documentation

- ESP32-S3 module: https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- ESP32-S3 GPIO limitations: https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html
- DS18B20 sensor family: https://www.analog.com/media/en/technical-documentation/data-sheets/DS18B20.pdf
- MAX30102 IC: https://www.analog.com/media/en/technical-documentation/data-sheets/MAX30102.pdf
- AD8232: https://www.analog.com/en/products/ad8232.html
