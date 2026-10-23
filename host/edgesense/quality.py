"""Explicit timing, dropouts and completeness; never infer missing samples from timestamps alone."""
from __future__ import annotations
from collections import defaultdict
from statistics import mean, median
from typing import Any, Iterable
from .io import MODES, FIELDS


def summarize(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        if rec.get("kind") == "sample":
            buckets[(rec["session"], rec["mode"])].append(rec)
    results = []
    for (session, mode), items in sorted(buckets.items()):
        # host receives data in serial order; re-sorting would obscure out-of-order frames
        seqs = [x["seq"] for x in items]
        ms = [x["uptime_ms"] for x in items]
        missing_seq = sum(max(0, b-a-1) for a,b in zip(seqs, seqs[1:]))
        duplicate_or_reordered = sum(b<=a for a,b in zip(seqs, seqs[1:]))
        invalid_time_steps = sum(b<=a for a,b in zip(ms, ms[1:]))
        diffs = [b-a for a,b in zip(ms, ms[1:]) if b > a]
        duration_s = (ms[-1]-ms[0])/1000 if len(ms)>1 else 0.0
        completeness = {}
        for sensor in MODES[mode]:
            for field in FIELDS[sensor]:
                present = sum(1 for r in items if r[sensor][field] is not None)
                completeness[f"{sensor}.{field}"] = round(present/len(items), 4)
        new_contact = sum(1 for r in items if r.get("thermal", {}).get("contact_new") is True)
        results.append({
            "session":session,"mode":mode,"received_frames":len(items),
            "lost_sequence_numbers_lower_bound":missing_seq,
            "duplicates_or_reordered":duplicate_or_reordered,
            "nonmonotonic_time_steps":invalid_time_steps,
            "duration_s":round(duration_s,3),
            "effective_frame_rate_hz":round((len(items)-1)/duration_s,3) if duration_s>0 else None,
            "median_interframe_ms":round(median(diffs),2) if diffs else None,
            "mean_interframe_ms":round(mean(diffs),2) if diffs else None,
            "field_valid_fraction":completeness,
            "new_contact_conversion_frames":new_contact if mode == "environment" else None,
        })
    return {"schema":1,"analysis":"transport_and_observation_quality_only","session_reports":results,
            "warnings":["No synchronization to UTC can be guaranteed by device uptime alone.",
                        "Sequence gaps detect loss AFTER firmware frame creation; sensor FIFO losses need separate counters.",
                        "A valid numeric field does not prove calibration or physiological correctness.",
                        "DS18B20 contact_c is a cached last value; use contact_new and contact_age_ms to assess actual conversion freshness."]}
