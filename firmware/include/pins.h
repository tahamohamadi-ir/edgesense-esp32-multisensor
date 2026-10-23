#pragma once
// PROVISIONAL PIN MAP: visually inferred from photographed N16R8 CAM board.
// Verify precise PCB pin mapping/voltage and camera/SD resource conflicts first.
// GPIO1 / GPIO14 / GPIO21 were proposed for a camera-free first experiment.
#define EDGE_I2C_SDA 1
#define EDGE_I2C_SCL 14
#define EDGE_ONEWIRE_PIN 21
#define EDGE_SERIAL_BAUD 115200
