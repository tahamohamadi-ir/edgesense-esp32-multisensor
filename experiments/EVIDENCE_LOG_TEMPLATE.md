# Hardware evidence ledger (fill only after real tests)

| Field | Required evidence |
|---|---|
| Date/time | Local date, time zone, UTC where relevant |
| Firmware version | Git commit SHA, PlatformIO profile |
| Device identity | Visible PCB photo, chip ID, boot log |
| Supply | measured VCC and logic high; multimeter and range |
| Wiring | GPIO label, verified schematic or continuity results |
| Sensor identity | I²C address + WHO_AM_I/functional plausibility; probe ROM for OneWire |
| Environment | ambient conditions / setup geometry, distances, material/emissivity assumptions |
| Session | anonymized ID, duration, operator annotations and phase labels |
| Integrity | report JSON, out-of-order/sequence-gap counts, dropped samples, reboot count |
| Measurement validity | any known reference reading and uncertainty; if none write NONE |
| Model evidence | complete train/validation/test sessions, metric denominators, code version |
| Data permissions | whether raw or anonymized output may be shared; biometric data private by default |

**Do not place secret credentials, personal PPG/ECG data, precise location, or proprietary workplace datasets in public commits.**
