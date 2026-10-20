"""Shared scoring for Build my Fast 50.

One place for the numbers so ledger.py (preview) and build_fast50.py (the file)
rank people the same way. Relationship strength is worked out from counts the
sweep recorded; fit is the label Claude gives each person against the investor
profile. Both are explained for the client in references/ranking-and-angles.md.

Standard library only. Decided October 13, 2026 for plugin v1.0.0.
"""

from datetime import date, datetime

RELATIONSHIP_LABELS = ("Strong", "Warm", "Dormant", "Thin")
FIT_LABELS = ("High", "Medium", "Low", "Unknown")
FIT_POINTS = {"High": 40, "Medium": 25, "Unknown": 12, "Low": 0, "": 12}

OUTPUT_COLUMNS = [
    "Name",
    "Email",
    "Company",
    "Title",
    "Last contact",
    "Relationship",
    "Fit",
    "Why they are a fit",
    "Suggested angle",
    "Source",
]


def parse_date(value):
    """Return a date from an ISO string, a datetime, or a date. None when it does not parse."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    # Full ISO timestamps (2026-08-14T09:30:00Z, with or without an offset) first.
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    # Then the plain forms the exports use: LinkedIn writes "02 Jan 2024",
    # Google and Outlook write m/d/yyyy, and the ledger writes yyyy-mm-dd.
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def months_between(earlier, later):
    """Whole months from earlier to later, floored at zero."""
    if earlier is None or later is None:
        return None
    months = (later.year - earlier.year) * 12 + (later.month - earlier.month)
    if later.day < earlier.day:
        months -= 1
    return max(months, 0)


def latest(*values):
    """The most recent of several date-like values, as a date, or None."""
    dates = [d for d in (parse_date(v) for v in values) if d is not None]
    return max(dates) if dates else None


def relationship_points(person, today=None):
    """0 to 60 points from recency, two-way traffic, frequency and meetings.

    Recency (0 to 20): a conversation this quarter is worth far more than one from
    two years back. Two-way (0 to 15): the client wrote and the person wrote back,
    which separates a relationship from a one-sided inbox. Frequency (0 to 12): how
    many separate threads. Meetings (0 to 13): calendar time together, which is the
    strongest single signal.
    """
    today = today or date.today()
    last = latest(person.get("last_contact"), person.get("last_meeting"))
    gap = months_between(last, today)
    if gap is None:
        recency = 0
    elif gap < 3:
        recency = 20
    elif gap < 6:
        recency = 16
    elif gap < 12:
        recency = 12
    elif gap < 18:
        recency = 7
    else:
        recency = 3

    they = int(person.get("they_wrote") or 0)
    you = int(person.get("you_wrote") or 0)
    if they and you:
        two_way = 15
    elif they:
        two_way = 5
    elif you:
        two_way = 3
    else:
        two_way = 0

    threads = int(person.get("threads") or 0)
    if threads >= 9:
        frequency = 12
    elif threads >= 4:
        frequency = 8
    elif threads >= 2:
        frequency = 4
    else:
        frequency = 0

    meetings = int(person.get("meetings") or 0)
    if meetings >= 4:
        met = 13
    elif meetings >= 2:
        met = 9
    elif meetings == 1:
        met = 6
    else:
        met = 0

    return recency + two_way + frequency + met


def relationship_label(person, today=None):
    """Strong, Warm, Dormant or Thin.

    Dormant is checked first: a real past relationship (two-way mail or a meeting)
    that has gone quiet for a year is its own thing, and Marcin's Fast 50 treats it
    as a reconnection, not a cold contact.
    """
    today = today or date.today()
    points = relationship_points(person, today)
    last = latest(person.get("last_contact"), person.get("last_meeting"))
    gap = months_between(last, today)
    two_way = bool(int(person.get("they_wrote") or 0) and int(person.get("you_wrote") or 0))
    met = int(person.get("meetings") or 0) > 0
    had_relationship = two_way or met
    if had_relationship and gap is not None and gap >= 12:
        return "Dormant"
    # Strong and Warm both need a real exchange: one inbound email with no reply
    # is not a relationship, however recent it is.
    if had_relationship and points >= 40:
        return "Strong"
    if had_relationship and points >= 22:
        return "Warm"
    return "Thin"


def fit_label(value):
    """Normalize a fit value to one of the four labels; blank becomes Unknown."""
    text = str(value or "").strip().capitalize()
    return text if text in FIT_LABELS else "Unknown"


def total_score(person, today=None):
    """Relationship points plus fit points, with two corrections.

    A Thin contact keeps at most 10 relationship points: one inbound email last
    week is recent, but it is not a relationship and must not outrank a plausible
    investor from the export. A Low fit earns nothing for fit and halves the
    relationship points, so people who do not fit the profile sink to the bottom
    while staying in the file for the client to see.
    """
    rel = relationship_points(person, today)
    label = relationship_label(person, today)
    fit = fit_label(person.get("fit"))
    if label == "Thin":
        rel = min(rel, 10)
    if fit == "Low":
        rel = rel // 2
    return rel + FIT_POINTS.get(fit, 12)


def sort_key(person, today=None):
    """Highest score first, then the most recent contact, then the name."""
    last = latest(person.get("last_contact"), person.get("last_meeting"), person.get("connected_on"))
    return (-total_score(person, today), -(last.toordinal() if last else 0), (person.get("name") or "").lower())
