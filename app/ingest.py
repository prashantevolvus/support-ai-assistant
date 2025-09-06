from __future__ import annotations

import csv
import io
import json
from typing import Iterable, Tuple


def parse_text_file(content: bytes, encoding: str = "utf-8") -> str:
    return content.decode(encoding, errors="ignore")


def parse_json_tickets(content: bytes) -> Iterable[Tuple[str | None, str, str, dict | None]]:
    data = json.loads(content.decode("utf-8", errors="ignore"))
    if isinstance(data, dict):
        data = [data]
    for item in data:
        ext_id = item.get("external_id") or item.get("id")
        title = item.get("title") or item.get("subject") or ""
        body = item.get("body") or item.get("description") or ""
        meta = item.get("metadata") or None
        yield ext_id, title, body, meta


def parse_csv_tickets(content: bytes) -> Iterable[Tuple[str | None, str, str, dict | None]]:
    text = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        ext_id = row.get("external_id") or row.get("id")
        title = row.get("title") or row.get("subject") or ""
        body = row.get("body") or row.get("description") or ""
        # Optional: capture any extra columns as metadata
        meta = {k: v for k, v in row.items() if k not in {"external_id", "id", "title", "subject", "body", "description"}}
        meta = meta or None
        yield ext_id, title, body, meta

