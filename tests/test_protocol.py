import json
import pytest
from edgesense.cli import simulate, audit
from edgesense.io import parse_line, SampleError
from edgesense.quality import summarize


def test_simulator_produces_explicitly_synthetic_records(tmp_path):
    src = tmp_path / "sim.jsonl"
    simulate(src,"environment",40,42)
    first, second = src.read_text().splitlines()[:2]
    assert parse_line(first)["synthetic"] is True
    assert parse_line(second)["synthetic"] is True
    qa = audit(src, tmp_path / "qa.json")
    assert qa["contains_synthetic_data"] is True
    assert qa["session_reports"][0]["received_frames"] == 40
    assert qa["session_reports"][0]["field_valid_fraction"]["thermal.contact_c"] == .5


def test_ppg_simulator(tmp_path):
    src=tmp_path/"fixture.jsonl"
    simulate(src,"ppg_motion",50,5)
    qa=audit(src,tmp_path/"report.json")
    assert qa["session_reports"][0]["field_valid_fraction"]["ppg.ir"]<1.0


def test_out_of_order_and_sequence_gaps_are_not_silent(tmp_path):
    src=tmp_path/"fixture.jsonl";simulate(src,"environment",3,10)
    entries=[json.loads(line) for line in src.read_text().splitlines()]
    entries[2]["seq"]=3
    entries[3]["seq"]=3
    report=summarize(entries)
    part=report["session_reports"][0]
    assert part["lost_sequence_numbers_lower_bound"]==2
    assert part["duplicates_or_reordered"]==1


def test_invalid_values_rejected():
    item={"schema":1,"kind":"sample","mode":"environment","session":"a","seq":0,"uptime_ms":0,
      "imu":{key:0 for key in ("ax_mps2","ay_mps2","az_mps2","gx_rads","gy_rads","gz_rads")},
      "thermal":{"object_c":None,"ambient_c":None,"contact_c":None}}
    assert parse_line(json.dumps(item))["kind"]=="sample"
    item["imu"]["ax_mps2"]="nan"
    with pytest.raises(SampleError):parse_line(json.dumps(item))


def test_wrong_schema_rejected():
    with pytest.raises(SampleError):parse_line('{"kind":"sample","schema":2}')
