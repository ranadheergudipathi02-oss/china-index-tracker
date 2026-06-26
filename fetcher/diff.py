"""Diff engine: compare new constituents vs the previous snapshot,
emit append-only change records. Membership identity is the symbol (6-digit ticker).
Names are carried for readability; a name-only change is NOT a membership change.
"""
import json
import config as C


def compute_diff(old_members, new_members):
    old = {m["symbol"]: m for m in old_members}
    new = {m["symbol"]: m for m in new_members}
    added = [{"symbol": s, "name": new[s].get("name", "")} for s in new if s not in old]
    removed = [{"symbol": s, "name": old[s].get("name", "")} for s in old if s not in new]
    return added, removed


def append_change(entry):
    with open(C.CHANGES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def make_entry(date_str, index_id, type_, added, removed):
    return {"date": date_str, "index": index_id, "type": type_,
            "added": added, "removed": removed}
