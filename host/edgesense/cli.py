"""Capture ESP32 JSONL, simulate unmistakably synthetic fixtures, generate quality reports."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import sys
import time
from .io import parse_line, SampleError
from .quality import summarize
from .features import window_features


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def simulate(out: Path, mode: str, frames: int, seed: int) -> None:
    if frames < 2: raise ValueError("frames must be >= 2")
    rng = random.Random(seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w",encoding="utf-8",newline="\n") as f:
        f.write(json.dumps({"kind":"boot","schema":1,"session":"SYNTHETIC-001", "synthetic":True})+"\n")
        for i in range(frames):
            # Artificial values for parser tests only, NOT a physical device model.
            frame={"kind":"sample","schema":1,"mode":mode,"session":"SYNTHETIC-001",
                   "seq":i,"uptime_ms":i*(50 if mode=="environment" else 20),"synthetic":True,
                   "imu":{"ax_mps2":rng.uniform(-.15,.15),"ay_mps2":rng.uniform(-.15,.15),
                          "az_mps2":9.81+rng.uniform(-.15,.15),"gx_rads":0.0,"gy_rads":0.0,"gz_rads":0.0}}
            if mode=="environment":
                frame["thermal"]={"object_c":25+rng.uniform(-.1,.1),"ambient_c":23.5,"contact_c":None if i<20 else 24.8, "contact_new": i>=20 and i%20==0,
                                  "contact_age_ms":None if i<20 else (i%20)*50}
            else:
                frame["ppg"]={"red":rng.randrange(1000,2500),"ir":None if i%9==0 else rng.randrange(1000,2500)}
            f.write(json.dumps(frame,separators=(",",":"),allow_nan=False)+"\n")

def audit(src: Path, out: Path) -> dict:
    records=[]; errors=[]; synthetic_count=0
    with src.open(encoding="utf-8") as f:
        for no,line in enumerate(f,1):
            if not line.strip():continue
            try:
                record=parse_line(line)
                records.append(record)
                synthetic_count+=bool(record.get("synthetic"))
            except SampleError as e:
                errors.append({"line":no,"error":str(e)[:150]})
    result=summarize(records)
    result.update({"source":str(src),"synthetic_records":synthetic_count,
                   "contains_synthetic_data":synthetic_count>0,
                   "invalid_lines":len(errors),"invalid_examples":errors[:20]})
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

def capture(port: str, out: Path, seconds: float, baud:int) -> None:
    if seconds<=0: raise ValueError("seconds must be > 0")
    try:
        import serial
    except ImportError as exc:
        raise RuntimeError('Install serial extra: pip install -e ".[serial]"') from exc
    out.parent.mkdir(parents=True,exist_ok=True)
    bad=0; good=0
    with serial.Serial(port,baud,timeout=1) as ser, out.open("w",encoding="utf-8",newline="\n") as f:
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            raw=ser.readline()
            if not raw: continue
            try:
                decoded=raw.decode("utf-8").strip()
                record=parse_line(decoded)
            except (UnicodeDecodeError,SampleError):
                bad+=1
                continue
            record["host_received_utc"]=utc_now()
            record["host_received_monotonic_ns"]=time.monotonic_ns()
            f.write(json.dumps(record,ensure_ascii=False,separators=(",",":"),allow_nan=False)+"\n")
            good+=1
    print(f"Captured {good} accepted frames; discarded {bad} malformed serial lines. Output: {out}")

def main(argv: list[str]|None=None) -> None:
    ap=argparse.ArgumentParser(prog="edgesense")
    commands=ap.add_subparsers(dest="cmd",required=True)
    sim=commands.add_parser("simulate",help="Generate distinctly synthetic test fixture")
    sim.add_argument("--out",type=Path,default=Path("data/synthetic/fixture.jsonl"))
    sim.add_argument("--mode",choices=["environment","ppg_motion"],default="environment")
    sim.add_argument("--frames",type=int,default=300)
    sim.add_argument("--seed",type=int,default=42)
    qa=commands.add_parser("audit",help="Generate quality report")
    qa.add_argument("--input",type=Path,required=True)
    qa.add_argument("--out",type=Path,default=Path("reports/quality.json"))
    fe=commands.add_parser("features",help="Extract labeled-as-descriptive window features")
    fe.add_argument("--input",type=Path,required=True)
    fe.add_argument("--out",type=Path,default=Path("reports/features.csv"))
    fe.add_argument("--window-ms",type=int,default=1000)
    cap=commands.add_parser("capture",help="Capture real UART frames (not simulated)")
    cap.add_argument("--port",required=True)
    cap.add_argument("--out",type=Path,default=Path("data/raw/capture.jsonl"))
    cap.add_argument("--seconds",type=float,default=60)
    cap.add_argument("--baud",type=int,default=115200)
    args=ap.parse_args(argv)
    if args.cmd=="simulate":simulate(args.out,args.mode,args.frames,args.seed); print(f"SYNTHETIC fixture -> {args.out}")
    if args.cmd=="audit":
        result=audit(args.input,args.out)
        print(f"valid sessions={len(result['session_reports'])}, invalid_lines={result['invalid_lines']}; report={args.out}")
    if args.cmd=="capture":capture(args.port,args.out,args.seconds,args.baud)
    if args.cmd=="features": print(f"Extracted {window_features(args.input,args.out,args.window_ms)} descriptive windows -> {args.out}")

if __name__=="__main__": main()
