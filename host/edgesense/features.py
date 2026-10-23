"""Generate descriptive sensor-window features; no unearned class/diagnostic labels."""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from .io import parse_line


def _stats(values:list[float]) -> tuple[float|None,float|None]:
    return (round(mean(values),5),round(pstdev(values),5)) if values else (None,None)

def window_features(src:Path, out:Path, window_ms:int=1000) -> int:
    if window_ms<100: raise ValueError("window_ms must be >= 100")
    groups={}
    with src.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():continue
            record=parse_line(line)
            if record["kind"]!="sample": continue
            key=(record["session"],record["mode"],record["uptime_ms"]//window_ms)
            groups.setdefault(key,[]).append(record)
    fieldnames=["session","mode","window_index","n_frames","start_uptime_ms","accel_norm_mean", "accel_norm_std", "gyro_norm_mean", "gyro_norm_std", "temp_diff_mean_c", "object_temp_mean_c", "ppg_ir_mean", "ppg_red_mean", "ppg_ir_valid_fraction", "synthetic"]
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames); writer.writeheader()
        for (session,mode,index),records in sorted(groups.items()):
            def mag(keys):
                result=[]
                for r in records:
                    vals=[r["imu"][k] for k in keys]
                    if all(v is not None for v in vals): result.append(math.sqrt(sum(v*v for v in vals)))
                return result
            an=_stats(mag(["ax_mps2","ay_mps2","az_mps2"]))
            gn=_stats(mag(["gx_rads","gy_rads","gz_rads"]))
            td=[]; ots=[]; irs=[]; reds=[]
            if mode=="environment":
                for r in records:
                    thermal=r["thermal"]
                    if thermal["object_c"] is not None: ots.append(thermal["object_c"])
                    if thermal["contact_c"] is not None and thermal["object_c"] is not None:
                        td.append(thermal["object_c"]-thermal["contact_c"])
            else:
                for r in records:
                    if r["ppg"]["ir"] is not None:irs.append(r["ppg"]["ir"])
                    if r["ppg"]["red"] is not None:reds.append(r["ppg"]["red"])
            writer.writerow({"session":session,"mode":mode,"window_index":index,
                             "n_frames":len(records),"start_uptime_ms":index*window_ms,
                             "accel_norm_mean":an[0],"accel_norm_std":an[1],
                             "gyro_norm_mean":gn[0],"gyro_norm_std":gn[1],
                             "temp_diff_mean_c":_stats(td)[0],"object_temp_mean_c":_stats(ots)[0],
                             "ppg_ir_mean":_stats(irs)[0],"ppg_red_mean":_stats(reds)[0],
                             "ppg_ir_valid_fraction":len(irs)/len(records) if mode=="ppg_motion" else None,
                             "synthetic":any(r.get("synthetic",False) for r in records)})
    return len(groups)
