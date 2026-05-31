"""JSON 文件读写，依赖 models。"""

import json
from pathlib import Path

from models import MonthData, Record


def _record_to_dict(r: Record) -> dict:
    return {
        "date": r.date.isoformat(),
        "start_time": r.start_time.isoformat(),
        "hours": r.hours,
        "class_type": r.class_type,
        "note": r.note,
    }


def _record_from_dict(d: dict) -> Record:
    from datetime import date, time

    return Record(
        date=date.fromisoformat(d["date"]),
        start_time=time.fromisoformat(d["start_time"]),
        hours=d["hours"],
        class_type=d["class_type"],
        note=d.get("note", ""),
    )


def save(filepath: str | Path, data: MonthData) -> None:
    payload = {
        "teacher_name": data.teacher_name,
        "records": [_record_to_dict(r) for r in data.records],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load(filepath: str | Path) -> MonthData:
    with open(filepath, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return MonthData(
        teacher_name=payload.get("teacher_name", ""),
        records=[_record_from_dict(d) for d in payload.get("records", [])],
    )
