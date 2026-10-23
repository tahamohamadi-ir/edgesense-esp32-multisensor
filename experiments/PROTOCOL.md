# Proposed validation and sensor-fusion experiments (not yet conducted)

## Task and outcomes

**Primary technical outcome:** percentage of usable frames per sensor field in repeat sessions, plus transport sequence gaps, median interframe spacing, sensor reporting time and reset counts. These are acquisition quality measures, **not direct physical measurement error**.

**Secondary task:** compare isolated sensing modalities with simple concatenated 1-second features on a *predefined event classification* problem, only after evidence supports independent session labels. No inference based on one sequence randomly divided into train/test.

## Planned bench sessions

| Condition | Experimental task | Intended reference | Minimum repetition |
|---|---|---|---|
| E0 | stationary device on bench | fixed stationary phase label | ≥3 distinct sessions |
| E1 | guided rotation and translation by hand | manually timed motion periods | ≥3 distinct sessions |
| E2 | safe, mild warmed object approaching IR module | independently logged object/proximity stage | ≥3 distinct sessions |
| E3 | one sensor disconnected with USB unplugged before each rewire | explicit sensor-disconnect condition log | ≥3 distinct sessions |
| P0 | optical sensor shielded from ambient light without human subject | controlled bench optical condition | ≥3 distinct sessions |
| P1 | optical sensor mechanically perturbed without being body-attached | manually marked bench movement condition | ≥3 distinct sessions |

**Labels:** log trial_id, independently observed manipulation, start/end device-uptime reference or host event, and uncertainty. Neither `imu` nor `ppg` values alone are ground truth for an event they are used to predict.

## Quality gates and experimental design

1. Electrical inspection completed and pin map recorded.
2. I²C sensor IDs read and module output plausible in a calibration check.
3. No invalid values silently replaced by zero; missingness explicit.
4. NTP/RTC is not a substitute for device-time calibration. If matching independent clocks, implement a proper timing pulse/sync experiment and measure offsets.
5. Freeze sessions and label definitions before model selection. For any classifier, **split by complete sessions** (prefer device/time blocks); never mix windows from one session across train/test.
6. Classifier baseline: majority/constant prediction. Model candidates: logistic regression or random forest with training-only imputation. Compare IMU-only, temperature-only, feature-level fusion, and leave-one-modality-out only when labeled examples are sufficient.
7. Provide per-condition and per-session coverage, confusion matrices with denominators, precision/recall, macro-F1, and uncertainty across independent sessions. Inspect class imbalance and device drift.
8. Hardware failure and sensor-related omission must be tracked separately from serial transport loss. No claim of scientific novelty, clinical utility, manufacturing defect performance or generalization from a single board.

## Honest research-status template

```text
Hardware assembly: NOT YET TESTED
Verified sensor readings: NONE
Real participant / bench trial data: NONE
Model trained on real captures: NO
Systemic sensor dropout results: NOT YET AVAILABLE
Next gate: power/IO safety inspection and single-sensor bring-up
```

This file is a plan, not an experimental report.
