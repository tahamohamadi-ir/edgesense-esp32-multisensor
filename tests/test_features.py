import csv
import pytest
from edgesense.cli import simulate
from edgesense.features import window_features


def test_feature_windows(tmp_path):
    src=tmp_path/"fixture.jsonl";out=tmp_path/"features.csv"
    simulate(src,"environment",40,42)
    assert window_features(src,out,1000)==2
    with out.open() as f: data=list(csv.DictReader(f))
    assert len(data)==2
    assert data[0]["synthetic"]=="True"
    assert data[0]["accel_norm_mean"]


def test_reject_invalid_windows(tmp_path):
    with pytest.raises(ValueError):window_features(tmp_path/"x",tmp_path/"out",0)
