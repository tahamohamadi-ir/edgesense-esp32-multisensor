# Applicant-reported component inventory — 23 October 2026

**Provenance:** consolidated from a detailed user-provided inventory reportedly based on 66 photographs and earlier purchase notes. Only a smaller subset of board photographs was directly available in this conversation. "Identified" describes visible labeling or vendor-matched family **not electrical testing, authenticity, or quantity**.

| Component | Reported / observed identification | Proposed role | Verification before enabling |
|---|---|---|---|
| ESP32-S3 camera dev board | ESP32-S3-WROOM N16R8 marking; camera FPC, microSD, two USB-C | central controller | PCB schematic, flash and PSRAM live check, GPIO map, soldered headers |
| OV5640 camera flex | likely OV5640 based on purchase and flex markings | later optical context | FPC pinout, power and exact supported driver |
| Arduino UNO compatible SMD | UNO family; chip marking not fully read | secondary controller / reference | USB converter, bootloader, 5 V↔3.3 V logic boundary |
| MPU6050 on GY-521 | board markings identify IMU | motion/vibration acquisition | sensor identity (WHO_AM_I), supply/logic voltage, test movement |
| MLX90614/GY-906 | probable family, unknown variant | IR temperature | variant, field of view, supply, emissivity and SMBus compatibility |
| DS18B20 sealed probe | listed in purchase, not independently photographed | contact temperature | wire colors/pinout, sensor ROM, 4.7 kΩ pull-up, repeatability |
| MAX30102 breakout | board label identified | raw reflective PPG counts | actual breakout VIN, I²C logic levels, FIFO/sample-rate behavior |
| AD8232 ECG breakout | board and electrodes visible | **excluded from USB-powered body measurements** | appropriate medical/electrical isolation and qualified safety review |
| ADS1115 breakout | board label identified | future analog acquisition | 3.3 V operation, input range, mux sampling non-simultaneity |
| HY-SRF05 ultrasonic | label identified; not HC-SR04 | future distance | 5 V supply, level shift on Echo, test at safe voltage |
| PIR motion module | family likely HC-SR501; exact module unconfirmed | future presence event | VCC level, output level, time delays |
| Water Sensor (MH) | label identified | future leak detection experiment | safe supply, galvanic effects, no calibrated depth claims |
| 1.3-inch OLED I²C | marked `1.30 IIC V2.2`, controller uncertain | status | pin order / address / voltage / controller |
| LCD1602 I²C backpack | 1602 family + probable PCF8574 | alternate status display | backpack 5 V logic and pull-up compatibility |
| L298N dual-H bridge | IC/PCB identity | motor control later only | motor availability, separate supply, heatsink and flyback design |
| HW-131 breadboard supply | label identified | benchtop regulated rail | power and output voltage under load, never assume 3.3 V from jumpers alone |
| LX-LCBST charger/boost | label identified, adjustable boost | **not used in first experiments** | output adjustment, charge/current limits and battery protection |
| DVE DSA-030A-05S adapter | label 5 V, 3 A | future supply | polarity, connector, actual voltage |
| iLPOWER S-24-12 adapter | label 12 V, 2 A | later motor supply only | polarity and actual voltage; NEVER ESP32 GPIO |
| ANENG A3004 & 830 multimeters | packaging identified | verification instrument | probes, battery, units and calibrated performance unknown |
| breadboards, jumpers, headers | photographed; quantities not confirmed | prototype wiring | contact quality and soldering |
| resistor assortment | photographed | pull-ups and dividers | measure selected component; expected 4.7k DS18B20 pull-up |
| miscellaneous LEDs, pots, discretes | types/values mostly not identified | future training | do not assume part number from appearance |

## Experiment priority

1. Stage 0: USB-UART boot and `WHO_AM_I`-like I²C inventory without any other external power rails.
2. Stage 1: GY-521 alone on confirmed 3.3 V bus. Capture repeatable motion data.
3. Stage 2: inspect GY-906 electrical variant, then add non-contact temperature.
4. Stage 3: test DS18B20 after measuring resistive pull-up and probe wiring.
5. Stage 4: separately wire MAX30102 with validated breakout voltage and I²C compatibility; limit optical acquisition to bench-quality tests, no health claims.
6. Stage 5: ONLY after individual sensor evidence, investigate fusion and optional OLED/camera. Other sensors are future independent adapters.
