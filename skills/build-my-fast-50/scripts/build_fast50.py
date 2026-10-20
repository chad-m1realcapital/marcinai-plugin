#!/usr/bin/env python3
"""Write the Fast 50 spreadsheet from the ledger and any export files.

  python3 build_fast50.py people.json [exports.json] --client "Jane" --out "/mnt/user-data/outputs/Fast 50 - Jane - 2026-10-13.xlsx"
      [--judgments judgments.json] [--all-exports] [--csv]

What it does, in order:
  1. Loads the people in people.json (the ledger; dropped people stay out).
  2. Merges exports.json: a person already in the ledger gets their company,
     title and name filled in from the export; a person who is only in the
     export is added when their fit_hint or a judgment says they fit the profile,
     or when --all-exports is given. The rest of a big LinkedIn export is better
     uploaded in MarcinAI directly, where the overnight ranking handles volume.
  3. Applies judgments.json (fit, why_fit, angle, company, title) by email, or by
     exact name for export rows without an email.
  4. Scores and sorts everyone: relationship points from the counts, fit points
     from the label, highest first, then most recent contact.
  5. Writes one .xlsx with exactly these columns in this order:
     Name, Email, Company, Title, Last contact, Relationship, Fit, Why they are a fit, Suggested angle, Source
     and falls back to .csv with the same header when openpyxl is not available or --csv is given.
  6. Prints a summary to paste into the chat.

Standard library plus openpyxl when present. Decided October 13, 2026 for plugin v1.0.0.
"""

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fast50_scoring as scoring  # noqa: E402

GENERIC_WHY = {
    "High": "Export only, no mail or calendar history in the last 24 months. Title or company reads as an investor or capital partner: {title_company}.",
    "Medium": "Export only, no mail or calendar history in the last 24 months. Title or company suggests the means or the reach to invest: {title_company}.",
    "Low": "Export only, no recent history and no profile match.",
    "Unknown": "Export only, no recent history. Nothing in the title or company to judge fit by.",
}
GENERIC_ANGLE = {
    "High": "Reconnect with a short personal note on where you both are now, then ask what they are investing in this year before you mention your raise.",
    "Medium": "Reconnect with a short personal note, share one line on what you are building, and ask who in their circle invests in deals like yours.",
    "Low": "Hold for a later wave; a general update when there is news to share.",
    "Unknown": "Hold for a later wave; a general update when there is news to share.",
}


def load_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def norm(text):
    return " ".join(str(text or "").lower().split())


def merge_exports(people, exports, include_all):
    by_email = {p["email"]: p for p in people if p.get("email")}
    by_name = {}
    for p in people:
        if p.get("name"):
            by_name.setdefault(norm(p["name"]), p)
    added = enriched = held_back = 0
    for row in exports:
        email = str(row.get("email") or "").lower().strip()
        target = by_email.get(email) if email else None
        if target is None and row.get("name"):
            target = by_name.get(norm(row["name"]))
        source = row.get("source") or "Contacts export"
        if target is not None:
            for field in ("company", "title", "name"):
                if not target.get(field) and row.get(field):
                    target[field] = row[field]
            if not target.get("connected_on") and row.get("connected_on"):
                target["connected_on"] = row["connected_on"]
            for s in source.split(" + "):
                if s not in target.setdefault("sources", []):
                    target["sources"].append(s)
            enriched += 1
            continue
        hint = scoring.fit_label(row.get("fit_hint")) if row.get("fit_hint") else ""
        if not include_all and not hint and not row.get("fit"):
            held_back += 1
            continue
        person = {
            "email": email, "name": row.get("name", ""), "company": row.get("company", ""), "title": row.get("title", ""),
            "first_contact": "", "last_contact": "", "last_meeting": "", "connected_on": row.get("connected_on", ""),
            "threads": 0, "they_wrote": 0, "you_wrote": 0, "meetings": 0, "topics": [],
            "sources": source.split(" + "), "fit": row.get("fit") or hint, "why_fit": row.get("why_fit", ""),
            "angle": row.get("angle", ""), "export_only": True,
        }
        people.append(person)
        if email:
            by_email[email] = person
        if person["name"]:
            by_name.setdefault(norm(person["name"]), person)
        added += 1
    return added, enriched, held_back


def apply_judgments(people, judgments):
    by_email = {p["email"]: p for p in people if p.get("email")}
    by_name = {}
    for p in people:
        if p.get("name"):
            by_name.setdefault(norm(p["name"]), p)
    applied = missed = 0
    for j in judgments:
        target = by_email.get(str(j.get("email") or "").lower().strip()) or by_name.get(norm(j.get("name")))
        if target is None:
            missed += 1
            continue
        for key in ("fit", "why_fit", "angle", "company", "title", "name"):
            if key in j and j[key] is not None and str(j[key]).strip():
                target[key] = scoring.fit_label(j[key]) if key == "fit" else str(j[key]).strip()
        applied += 1
    return applied, missed


def fill_generic_lines(person):
    """Export-only rows Claude did not judge still get an honest line each."""
    if not person.get("export_only"):
        return
    fit = scoring.fit_label(person.get("fit"))
    title_company = ", ".join(x for x in (person.get("title"), person.get("company")) if x) or "not stated"
    if not person.get("why_fit"):
        person["why_fit"] = GENERIC_WHY[fit].format(title_company=title_company)
    if not person.get("angle"):
        person["angle"] = GENERIC_ANGLE[fit]


def to_row(person, today):
    last = scoring.latest(person.get("last_contact"), person.get("last_meeting"))
    if last is None and person.get("export_only"):
        last = scoring.parse_date(person.get("connected_on"))
    return [
        person.get("name") or "",
        person.get("email") or "",
        person.get("company") or "",
        person.get("title") or "",
        last.isoformat() if last else "",
        scoring.relationship_label(person, today),
        scoring.fit_label(person.get("fit")),
        person.get("why_fit") or "",
        person.get("angle") or "",
        " + ".join(person.get("sources") or []),
    ]


def write_xlsx(rows, out):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Fast 50"
    ws.append(scoring.OUTPUT_COLUMNS)
    for row in rows:
        ws.append(row)
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", start_color="1F2937", end_color="1F2937")
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(vertical="center")
    widths = [26, 32, 24, 26, 13, 13, 10, 60, 60, 22]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    wrap = Alignment(wrap_text=True, vertical="top")
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = wrap
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wb.save(out)


def write_csv(rows, out):
    with Path(out).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(scoring.OUTPUT_COLUMNS)
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Write the Fast 50 spreadsheet")
    parser.add_argument("ledger", help="people.json from ledger.py")
    parser.add_argument("exports", nargs="?", help="exports.json from parse_exports.py (optional)")
    parser.add_argument("--client", default="", help="the client's first name or company, used in the summary")
    parser.add_argument("--out", required=True, help="output path ending in .xlsx (or .csv)")
    parser.add_argument("--judgments", help="judgments.json to apply to ledger and export rows")
    parser.add_argument("--all-exports", action="store_true", help="include every export row, not only profile matches")
    parser.add_argument("--csv", action="store_true", help="write .csv instead of .xlsx")
    args = parser.parse_args(argv)

    today = date.today()
    ledger = load_json(args.ledger)
    people = list((ledger.get("people") or {}).values()) if isinstance(ledger, dict) else list(ledger)
    dropped = len(ledger.get("dropped") or {}) if isinstance(ledger, dict) else 0

    added = enriched = held_back = 0
    if args.exports:
        added, enriched, held_back = merge_exports(people, load_json(args.exports), args.all_exports)
    applied = missed = 0
    if args.judgments:
        applied, missed = apply_judgments(people, load_json(args.judgments))
    for p in people:
        fill_generic_lines(p)

    people.sort(key=lambda p: scoring.sort_key(p, today))
    rows = [to_row(p, today) for p in people]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wrote = out
    if args.csv or out.suffix.lower() == ".csv":
        wrote = out.with_suffix(".csv")
        write_csv(rows, wrote)
    else:
        try:
            write_xlsx(rows, out)
        except ImportError:
            wrote = out.with_suffix(".csv")
            write_csv(rows, wrote)
            print("openpyxl is not available here, so the file is .csv (MarcinAI's importer takes either).")

    rel = Counter(r[5] for r in rows)
    fit = Counter(r[6] for r in rows)
    sources = Counter()
    for r in rows:
        for s in r[9].split(" + "):
            if s:
                sources[s] += 1
    unjudged = sum(1 for p in people if not p.get("fit") and not p.get("export_only"))
    who = f" for {args.client}" if args.client else ""
    print(f"Wrote {wrote} with {len(rows)} people{who}.")
    print("By source: " + ", ".join(f"{k} {v}" for k, v in sources.most_common()) + ".")
    print("Relationship: " + ", ".join(f"{k} {rel.get(k, 0)}" for k in scoring.RELATIONSHIP_LABELS) + ".")
    print("Fit: " + ", ".join(f"{k} {fit.get(k, 0)}" for k in scoring.FIT_LABELS) + ".")
    if args.exports:
        print(f"Exports: {enriched} people enriched, {added} export-only people added, {held_back} held back (no profile match; upload the export in MarcinAI to add them all).")
    if args.judgments:
        print(f"Judgments applied: {applied}; not matched: {missed}.")
    if dropped:
        print(f"Dropped during cleaning: {dropped} (automated senders, the client's own addresses, colleagues).")
    if unjudged:
        print(f"Still unjudged from mail or calendar: {unjudged}. They are in the file as Fit Unknown; judge them and rebuild if there is time.")
    print("Top 10:")
    for i, r in enumerate(rows[:10], 1):
        print(f"  {i}. {r[0] or r[1]} ({r[5]}, {r[6]}): {r[7][:90]}")


if __name__ == "__main__":
    main()
