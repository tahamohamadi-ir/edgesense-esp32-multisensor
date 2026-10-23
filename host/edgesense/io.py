"""Schema guards and device-frame parsing. Use strict JSON, no eval or coercion."""
from __future__ import annotations
import json
import math
from typing import Any

class SampleError(ValueError):
    """Invalid transport payload, distinct from absent sensor readings."""

FIELDS = {
    "imu": ("ax_mps2", "ay_mps2", "az_mps2", "gx_rads", "gy_rads", "gz_rads"),
    "thermal": ("object_c", "ambient_c", "contact_c"),
    "ppg": ("red", "ir"),
}
MODES = {"environment": ("imu", "thermal"), "ppg_motion": ("imu", "ppg")}

def parse_line(line: str) -> dict[str, Any]:
    try:
        data = json.loads(line)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SampleError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise SampleError("unsupported schema")
    if data.get("kind") == "boot":
        if not isinstance(data.get("session"), str):
            raise SampleError("boot without session")
        return data
    if data.get("kind") != "sample" or data.get("mode") not in MODES:
        raise SampleError("unexpected record kind/mode")
    if not isinstance(data.get("session"), str) or not data["session"]:
        raise SampleError("invalid session")
    for key in ("seq", "uptime_ms"):
        if isinstance(data.get(key), bool) or not isinstance(data.get(key), int) or data[key] < 0:
            raise SampleError(f"invalid {key}")
    for sensor in MODES[data["mode"]]:
        values = data.get(sensor)
        if not isinstance(values, dict):
            raise SampleError(f"missing sensor object: {sensor}")
        for key in FIELDS[sensor]:
            value = values.get(key, "__not_found__")
            if value == "__not_found__":
                raise SampleError(f"absent field: {sensor}.{key}")
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)):
                raise SampleError(f"nonfinite/non-numeric reading: {sensor}.{key}")
    return data
