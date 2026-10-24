#!/usr/bin/env python3
"""Read a LinkedIn connections export or a contacts export into exports.json.

Why a script: every export has its own shape and its own traps. LinkedIn puts
three note lines above the header, Google ships two different column sets, and
iPhone contacts come out of iCloud as a vCard, not a spreadsheet. Reading them
with one tested parser means the same file gives the same people every time.

  python3 parse_exports.py Connections.csv [contacts.csv contacts.vcf ...] --out exports.json
      [--keywords "multifamily,dentist,physician,Dallas"]

Each person comes out as:
  {"name": "Jane Doe", "email": "jane@doecapital.com", "company": "Doe Capital", "title": "Managing Partner",
   "connected_on": "2024-01-02", "source": "LinkedIn export", "fit_hint": "High"}

fit_hint is a first pass from the title and company only: "High" when the words
say investor, capital, fund, family office and the like; "Medium" for senior
professionals, owners and the client's own keywords; "" when nothing matched.
Claude confirms or changes it for the people who matter; build_fast50.py uses it
to decide which export-only people belong in the file.

Formats recognized: LinkedIn Connections.csv (First Name, Last Name, URL,
Email Address, Company, Position, Connected On), Google Contacts CSV (both the
older "Organization 1 - Name" layout and the newer "Organization Name" layout),
Outlook CSV (Company, Job Title, E-mail Address), vCard .vcf (FN, N, EMAIL,
ORG, TITLE), and any other CSV with a column that looks like a name and an email.

Standard library only. Decided October 13, 2026 for plugin v1.0.0.
"""

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fast50_scoring as scoring  # noqa: E402

# Matched inside " title company " in lowercase, so a leading space keeps
# " fund" from matching "refund" and " angel" from matching "Angela".
HIGH_WORDS = (
    "investor", "investment", "investing", " capital", "family office", "private equity", "equity partner",
    "equity investor", "equity fund", " venture", " fund ", " funds", "fund manager", "asset management", "wealth",
    "limited partner", "general partner", "syndicator", "syndication", "sponsor", "private lender", "hard money",
    "allocator", "endowment", "pension", "angel investor", " angel ", "hnw", "high net worth", "ultra high",
    "trust company", "real estate investor", "real estate developer", " reit", "capital partner", "co-gp", " lp ",
)
MEDIUM_WORDS = (
    "principal", "founder", "owner", "ceo", "chief executive", "president", "chairman", "managing director",
    "managing partner", "partner", "director", "vice president", "vp ", "svp", "evp", "cfo", "coo", "cto",
    "physician", "doctor", " md", "m.d.", "dds", "dmd", "dentist", "orthodontist", "surgeon", "anesthesiologist",
    "radiologist", "dermatologist", "cardiologist", "pharmacist", "veterinarian", "optometrist", "chiropractor",
    "attorney", "lawyer", "counsel", "esq", "cpa", "accountant", "financial advisor", "financial planner",
    "wealth advisor", "broker", "realtor", "real estate", "multifamily", "acquisitions", "developer", "entrepreneur",
    "executive", "engineer", "pilot", "consultant", "architect", "professor", "retired", "business owner",
    "franchise", "operator", "general contractor", "property manager", "escrow", "insurance", "mortgage", "lender",
    "lending", "banker", " bank", "credit union", "1031", "self-directed", " ira", "retirement", "sales director",
    "practice owner",
)

CSV_ENCODINGS = ("utf-8-sig", "utf-16", "utf-8", "cp1252", "latin-1")


def read_text(path):
    raw = Path(path).read_bytes()
    for enc in CSV_ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def norm_email(value):
    text = str(value or "").strip().lower()
    match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
    return match.group(0) if match else ""


def squash(value):
    return re.sub(r"\s+", " ", str(value or "").replace("\u00a0", " ")).strip()


def fit_hint(title, company, extra_words):
    """High from the title or the company (a firm called X Capital is a signal on its
    own); Medium from the title only, since "Acme Software" says nothing about the
    analyst who works there; the client's own words count wherever they appear."""
    both = f" {title} {company} ".lower()
    title_text = f" {title} ".lower()
    if any(w in both for w in HIGH_WORDS):
        return "High"
    if any(w in title_text for w in MEDIUM_WORDS) or any(w and w.lower() in both for w in extra_words):
        return "Medium"
    return ""


def iso(value):
    d = scoring.parse_date(value)
    return d.isoformat() if d else ""


def find_header_line(text):
    """LinkedIn writes three note lines above the header; find the real header row."""
    lines = text.splitlines()
    for i, line in enumerate(lines[:15]):
        low = line.lower()
        if ("first name" in low and "last name" in low) or ("name" in low and "e-mail" in low) or ("name" in low and "email" in low):
            return "\n".join(lines[i:])
    return text


HONORIFICS = {"mr", "mrs", "ms", "miss", "mx", "dr", "prof", "rev", "sir", "madam"}


def col(row, *names):
    """First non-empty value among candidate column names, matched case-insensitively."""
    lowered = {k.strip().lower(): v for k, v in row.items() if k}
    for name in names:
        value = lowered.get(name.lower())
        if value and str(value).strip():
            return squash(value)
    return ""


def parse_csv(path, extra_words):
    text = find_header_line(read_text(path))
    reader = csv.DictReader(io.StringIO(text))
    headers = [h.strip().lower() for h in (reader.fieldnames or []) if h]
    if "connected on" in headers and "position" in headers:
        source = "LinkedIn export"
    elif any(h.startswith("organization 1") or h == "organization name" for h in headers) or "e-mail 1 - value" in headers:
        source = "Google export"
    elif "e-mail address" in headers and ("job title" in headers or "company" in headers):
        source = "Outlook export"
    else:
        source = "Contacts export"
    people = []
    for row in reader:
        first = col(row, "First Name", "Given Name", "First")
        last = col(row, "Last Name", "Family Name", "Last")
        name = squash(f"{first} {last}") or col(row, "Name", "Full Name", "Display Name")
        email = norm_email(col(row, "Email Address", "E-mail Address", "E-mail 1 - Value", "E-mail 2 - Value",
                                "E-mail 2 Address", "E-mail 3 Address", "Email", "Email 1", "Primary Email", "Work Email"))
        if not email:
            # Any column with "mail" in its name, for odd spreadsheets.
            for key, value in row.items():
                if key and "mail" in key.lower() and norm_email(value):
                    email = norm_email(value)
                    break
        company = col(row, "Company", "Organization Name", "Organization 1 - Name", "Organization", "Employer", "Company Name")
        title = col(row, "Position", "Job Title", "Organization Title", "Organization 1 - Title", "Title", "Role")
        if title.lower().rstrip(".") in HONORIFICS:
            # Outlook and Yahoo put Mr., Dr. and the like in a column called Title; that is not a job title.
            title = ""
        connected = iso(col(row, "Connected On", "Connected", "Date Added"))
        if not name and not email:
            continue
        people.append({
            "name": name, "email": email, "company": company, "title": title,
            "connected_on": connected, "source": source,
            "fit_hint": fit_hint(title, company, extra_words),
        })
    return people


def unfold_vcard(text):
    """vCard folds long lines; a continuation line starts with a space or tab."""
    out = []
    for line in text.splitlines():
        if line[:1] in (" ", "\t") and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def parse_vcard(path, extra_words):
    people = []
    current = None
    for line in unfold_vcard(read_text(path)):
        upper = line.upper()
        if upper.startswith("BEGIN:VCARD"):
            current = {"name": "", "email": "", "company": "", "title": "", "connected_on": "", "source": "Phone export"}
            continue
        if upper.startswith("END:VCARD"):
            if current and (current["name"] or current["email"]):
                current["fit_hint"] = fit_hint(current["title"], current["company"], extra_words)
                people.append(current)
            current = None
            continue
        if current is None or ":" not in line:
            continue
        key, _, value = line.partition(":")
        prop = key.split(";")[0].upper()
        value = squash(value.replace("\\,", ",").replace("\\;", ";"))
        if prop == "FN" and not current["name"]:
            current["name"] = value
        elif prop == "N" and not current["name"]:
            parts = value.split(";")
            current["name"] = squash(f"{parts[1] if len(parts) > 1 else ''} {parts[0]}")
        elif prop == "EMAIL" and not current["email"]:
            current["email"] = norm_email(value)
        elif prop == "ORG" and not current["company"]:
            current["company"] = value.split(";")[0]
        elif prop == "TITLE" and not current["title"]:
            current["title"] = value
    return people


def dedupe(people):
    """One row per email; without an email, one row per name and company."""
    seen = {}
    for p in people:
        key = p["email"] or ("name:" + p["name"].lower() + "|" + p["company"].lower())
        if key in seen:
            kept = seen[key]
            for field in ("name", "email", "company", "title", "connected_on"):
                if not kept.get(field) and p.get(field):
                    kept[field] = p[field]
            if p["fit_hint"] == "High" or (p["fit_hint"] == "Medium" and not kept["fit_hint"]):
                kept["fit_hint"] = p["fit_hint"]
            if p["source"] not in kept["source"]:
                kept["source"] = kept["source"] + " + " + p["source"]
        else:
            seen[key] = dict(p)
    return list(seen.values())


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read LinkedIn and contacts exports for Build my Fast 50")
    parser.add_argument("files", nargs="+", help="export files (.csv or .vcf)")
    parser.add_argument("--out", required=True, help="where to write exports.json")
    parser.add_argument("--keywords", default="", help="comma separated words from the investor profile, for the fit hint")
    args = parser.parse_args(argv)
    extra_words = [w.strip() for w in args.keywords.split(",") if w.strip()]
    people = []
    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"missing file: {f}", file=sys.stderr)
            continue
        if path.suffix.lower() == ".vcf":
            found = parse_vcard(path, extra_words)
        else:
            found = parse_csv(path, extra_words)
        print(f"{path.name}: {len(found)} people ({found[0]['source'] if found else 'no rows'})")
        people.extend(found)
    people = dedupe(people)
    with Path(args.out).open("w", encoding="utf-8") as f:
        json.dump(people, f, indent=1, ensure_ascii=False)
    with_email = sum(1 for p in people if p["email"])
    high = sum(1 for p in people if p["fit_hint"] == "High")
    medium = sum(1 for p in people if p["fit_hint"] == "Medium")
    print(f"Wrote {len(people)} people to {args.out}: {with_email} with an email address, "
          f"{high} look High fit and {medium} Medium fit from their title or company.")


if __name__ == "__main__":
    main()
