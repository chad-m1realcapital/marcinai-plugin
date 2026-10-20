#!/usr/bin/env python3
"""The people ledger for Build my Fast 50 (people.json).

Why a ledger: a 24 month mail sweep runs to hundreds of threads across many
search pages, and tallying them by hand loses count. Each page's observations
are added here, deduplicated by thread or event id, so the counts stay right no
matter how many pages the sweep takes or how many times a page is added.

Commands (run from anywhere; paths can be relative or absolute):

  python3 ledger.py add people.json observations.json
      Add mail threads and calendar events. observations.json is a JSON array:
        {"kind": "thread", "id": "<thread id>", "date": "2026-08-14", "topic": "LP returns",
         "you_wrote": true, "people": [{"email": "jane@doecapital.com", "name": "Jane Doe", "wrote": true}]}
        {"kind": "event", "id": "<event id>", "date": "2026-06-02", "title": "Coffee with Jane",
         "people": [{"email": "jane@doecapital.com", "name": "Jane Doe"}]}

  python3 ledger.py clean people.json --self you@example.com,alias@example.com [--skip-domain yourfirm.com] [--keep-domain partners.com]
      Drop automated senders, the client's own addresses and colleagues at the
      client's company domain. Dropped people are kept under "dropped" so they
      can be restored; the command prints what it dropped and why.

  python3 ledger.py judge people.json judgments.json
      Set fit, why_fit, angle, company, title or name per person. judgments.json is a JSON array:
        {"email": "jane@doecapital.com", "fit": "High", "why_fit": "...", "angle": "...", "company": "...", "title": "..."}
      Add "drop": true to drop someone instead.

  python3 ledger.py drop people.json email [email ...]
  python3 ledger.py restore people.json email [email ...]
  python3 ledger.py show people.json [--top 25]
      Preview the ranking the way build_fast50.py will write it.

Standard library only. Decided October 13, 2026 for plugin v1.0.0.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fast50_scoring as scoring  # noqa: E402

# Words in the part before @ that mark automated or role mail. A person counts
# when a human wrote in their own words; these addresses never do. The local
# part is split on dots, dashes, underscores and plus signs, so "no.reply.alerts@"
# and "notifications-123@" both hit while "abbott@" and "autumn@" do not.
JUNK_TOKENS = {
    "noreply", "donotreply", "notification", "notifications", "mailer", "daemon", "postmaster", "bounce", "bounces",
    "alert", "alerts", "digest", "newsletter", "newsletters", "news", "updates", "info", "hello", "team", "support",
    "help", "helpdesk", "billing", "invoice", "invoices", "receipts", "receipt", "accounting", "payments", "marketing",
    "promo", "promotions", "offers", "scheduling", "scheduler", "bookings", "reminders", "reminder", "feedback",
    "survey", "surveys", "unsubscribe", "jobs", "careers", "recruiting", "security", "admin", "webmaster", "system",
    "robot", "bot", "automated", "customerservice", "orders", "shipping", "tracking", "verify", "verification",
    "password", "welcome", "confirm", "confirmation", "notify", "community", "press", "legal", "privacy", "compliance",
    "subscriptions", "subscription", "membership", "store", "shop", "sales", "lists", "list", "calendar", "service",
    "contact", "accounts", "noreplies", "autoreply", "autoresponder", "donotreply", "dnr", "mailerdaemon",
}

# Domains that carry nothing but system mail: schedulers, e-sign, payments,
# notetakers, social sites, listing alerts, newsletter senders. Kept narrow on
# purpose: a banker at a bank or an engineer at Google is a real relationship,
# and their employer's automated mail is caught by the token rule above instead.
JUNK_DOMAINS = (
    "calendly.com", "oncehub.com", "scheduleonce.com", "acuityscheduling.com", "zoom.us",
    "docusign.net", "hellosign.com", "dropboxsign.com", "adobesign.com", "echosign.com",
    "facebookmail.com", "linkedin.com", "twitter.com", "x.com", "instagram.com", "tiktok.com", "youtube.com",
    "fathom.video", "fathom.ai", "otter.ai", "fireflies.ai", "read.ai", "tldv.io", "grain.com", "sembly.ai",
    "mailchimpapp.net", "mcsv.net", "rsgsv.net", "hubspotemail.net", "sendgrid.net", "ccsend.com",
    "constantcontact.com", "intercom-mail.com", "activehosted.com", "convertkit-mail.com", "convertkit-mail2.com",
    "substack.com", "beehiiv.com", "medium.com", "eventbrite.com", "meetup.com", "luma-mail.com",
    "zillow.com", "redfin.com", "realtor.com", "loopnet.com", "costar.com", "crexi.com", "apartments.com",
    "bisnow.com", "globest.com", "therealdeal.com", "nerdwallet.com", "creditkarma.com",
    "uber.com", "lyft.com", "doordash.com", "airbnb.com", "expedia.com", "godaddy.com", "namecheap.com",
    "squarespace.com", "wix.com", "spotify.com", "netflix.com", "venmo.com", "paypal.com", "stripe.com",
    "quickbooks.com", "intuit.com", "bill.com", "squareup.com", "atlassian.net", "claude.ai",
)

# Marketing and transactional mail usually comes from a sending subdomain such
# as email.company.com or news.company.com. People do not have addresses there.
# "mail." is left out because some universities give people mail.school.edu addresses.
SENDING_SUBDOMAINS = {
    "e", "em", "email", "emails", "news", "newsletter", "newsletters", "info", "hello", "marketing", "updates", "notify",
    "notifications", "alerts", "alert", "noreply", "no-reply", "bounce", "bounces", "reply", "go", "send", "t", "link",
    "links", "track", "click", "mg", "mta", "mailer", "campaign", "campaigns", "promo", "offers", "engage", "connect",
    "em1", "em2", "e1", "e2", "mail1", "mail2", "msg", "messages", "message", "notice", "notices", "digest",
}

# Public mail providers. An address at one of these is a person, never a
# colleague by domain, so the colleague rule skips them.
PUBLIC_MAIL_DOMAINS = (
    "gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "outlook.com", "hotmail.com", "live.com", "msn.com",
    "icloud.com", "me.com", "mac.com", "aol.com", "protonmail.com", "proton.me", "pm.me", "comcast.net", "att.net",
    "sbcglobal.net", "verizon.net", "cox.net", "charter.net", "earthlink.net", "zoho.com", "fastmail.com", "hey.com",
    "gmx.com", "mail.com", "yandex.com", "rogers.com", "bell.net", "shaw.ca", "telus.net", "sympatico.ca",
)

EMPTY = {"people": {}, "dropped": {}, "meta": {}}


def load(path):
    p = Path(path)
    if not p.exists():
        return json.loads(json.dumps(EMPTY))
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    for key in ("people", "dropped", "meta"):
        data.setdefault(key, {})
    return data


def save(path, data):
    data["meta"]["updated"] = date.today().isoformat()
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)


def norm_email(value):
    text = str(value or "").strip().lower()
    match = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
    return match.group(0) if match else ""


def clean_name(value, email=""):
    text = str(value or "").strip().strip('"').strip("'").strip()
    if not text or "@" in text or text.lower() == email.lower():
        return ""
    if "," in text and len(text.split(",")) == 2:
        last, first = (part.strip() for part in text.split(","))
        text = f"{first} {last}"
    return re.sub(r"\s+", " ", text)


def iso_date(value):
    d = scoring.parse_date(value)
    return d.isoformat() if d else ""


def blank_person(email):
    return {
        "email": email, "name": "", "company": "", "title": "",
        "first_contact": "", "last_contact": "", "last_meeting": "",
        "threads": 0, "they_wrote": 0, "you_wrote": 0, "meetings": 0,
        "topics": [], "sources": [], "fit": "", "why_fit": "", "angle": "",
        "seen": {"threads": [], "events": []},
    }


def better_name(current, new):
    """Keep the more complete name: more words, then longer."""
    if not new:
        return current
    if not current:
        return new
    cw, nw = len(current.split()), len(new.split())
    if nw > cw or (nw == cw and len(new) > len(current)):
        return new
    return current


def touch_dates(person, when, key="last_contact"):
    if not when:
        return
    if not person.get("first_contact") or when < person["first_contact"]:
        person["first_contact"] = when
    if not person.get(key) or when > person[key]:
        person[key] = when


def add_source(person, source):
    if source not in person["sources"]:
        person["sources"].append(source)


def cmd_add(args):
    data = load(args.ledger)
    with Path(args.observations).open(encoding="utf-8") as f:
        observations = json.load(f)
    if isinstance(observations, dict):
        observations = [observations]
    added_threads = added_events = skipped = 0
    for obs in observations:
        kind = (obs.get("kind") or "thread").lower()
        oid = str(obs.get("id") or "").strip()
        when = iso_date(obs.get("date"))
        if not oid:
            skipped += 1
            continue
        for who in obs.get("people") or []:
            email = norm_email(who.get("email"))
            if not email:
                continue
            bucket = "dropped" if email in data["dropped"] else "people"
            person = data[bucket].setdefault(email, blank_person(email))
            person["name"] = better_name(person.get("name", ""), clean_name(who.get("name"), email))
            seen_key = "events" if kind == "event" else "threads"
            if oid in person["seen"][seen_key]:
                continue
            person["seen"][seen_key].append(oid)
            if kind == "event":
                person["meetings"] += 1
                touch_dates(person, when, "last_meeting")
                touch_dates(person, when, "last_contact")
                add_source(person, "Calendar")
                title = str(obs.get("title") or "").strip()
                if title and title not in person["topics"] and len(person["topics"]) < 8:
                    person["topics"].append(title)
            else:
                person["threads"] += 1
                if who.get("wrote"):
                    person["they_wrote"] += 1
                if obs.get("you_wrote"):
                    person["you_wrote"] += 1
                touch_dates(person, when, "last_contact")
                add_source(person, "Mail")
                topic = str(obs.get("topic") or "").strip()
                if topic and topic not in person["topics"] and len(person["topics"]) < 8:
                    person["topics"].append(topic)
        if kind == "event":
            added_events += 1
        else:
            added_threads += 1
    save(args.ledger, data)
    print(f"Added {added_threads} threads and {added_events} events. "
          f"People in ledger: {len(data['people'])} (dropped: {len(data['dropped'])}). Skipped {skipped} observations with no id.")


def is_junk(email):
    """Return the reason an address is automated or role mail, or "" for a person."""
    local, _, domain = email.partition("@")
    local_base = local.split("+")[0]
    tokens = [t for t in re.split(r"[._\-]", local_base) if t]
    token_set = set(tokens)
    hit = token_set & JUNK_TOKENS
    if hit:
        return f"automated or role address ({sorted(hit)[0]})"
    if ("no" in token_set and "reply" in token_set) or ("do" in token_set and "not" in token_set and "reply" in token_set):
        return "automated address (no reply)"
    if re.fullmatch(r"[a-z0-9]{20,}", local_base) or re.search(r"\d{6,}", local_base):
        return "machine generated address"
    for junk in JUNK_DOMAINS:
        if domain == junk or domain.endswith("." + junk):
            return f"system mail from {junk}"
    labels = domain.split(".")
    if len(labels) >= 3 and labels[0] in SENDING_SUBDOMAINS:
        return f"marketing sender ({domain})"
    return ""


def cmd_clean(args):
    data = load(args.ledger)
    selves = {norm_email(e) for e in (args.self or "").split(",") if norm_email(e)}
    skip_domains = {d.strip().lower() for d in (args.skip_domain or "").split(",") if d.strip()}
    keep_domains = {d.strip().lower() for d in (args.keep_domain or "").split(",") if d.strip()}
    # The client's company domain is inferred from their own addresses unless given.
    if not skip_domains and not args.no_colleague_rule:
        for e in selves:
            domain = e.partition("@")[2]
            if domain and domain not in PUBLIC_MAIL_DOMAINS:
                skip_domains.add(domain)
    skip_domains -= keep_domains
    dropped = []
    for email in list(data["people"].keys()):
        reason = ""
        domain = email.partition("@")[2]
        if email in selves:
            reason = "the client's own address"
        elif domain in skip_domains and not args.no_colleague_rule:
            reason = f"colleague at {domain}"
        elif domain not in keep_domains:
            reason = is_junk(email)
        if reason:
            person = data["people"].pop(email)
            person["dropped_because"] = reason
            data["dropped"][email] = person
            dropped.append((email, reason))
    save(args.ledger, data)
    print(f"Dropped {len(dropped)}. People left: {len(data['people'])}.")
    if skip_domains:
        print("Colleague domains skipped: " + ", ".join(sorted(skip_domains)) + " (use --keep-domain to keep one, or restore people by email)")
    for email, reason in dropped:
        print(f"  {email}: {reason}")


def cmd_judge(args):
    data = load(args.ledger)
    with Path(args.judgments).open(encoding="utf-8") as f:
        judgments = json.load(f)
    if isinstance(judgments, dict):
        judgments = [judgments]
    by_name = {}
    for e, p in data["people"].items():
        if p.get("name"):
            by_name.setdefault(re.sub(r"\s+", " ", p["name"].lower().strip()), e)
    updated = missing = dropped = 0
    for j in judgments:
        email = norm_email(j.get("email"))
        if not email and j.get("name"):
            email = by_name.get(re.sub(r"\s+", " ", str(j["name"]).lower().strip()), "")
        person = data["people"].get(email)
        if person is None:
            missing += 1
            print(f"  not in ledger: {j.get('email') or j.get('name')} (export-only people are judged at build time through --judgments)")
            continue
        if j.get("drop"):
            person["dropped_because"] = str(j.get("why_fit") or j.get("reason") or "dropped during review")
            data["dropped"][email] = data["people"].pop(email)
            dropped += 1
            continue
        for key in ("fit", "why_fit", "angle", "company", "title", "name"):
            if key in j and j[key] is not None:
                value = str(j[key]).strip()
                if key == "fit":
                    value = scoring.fit_label(value)
                person[key] = value
        updated += 1
    save(args.ledger, data)
    print(f"Updated {updated}, dropped {dropped}, not found {missing}. Judged so far: "
          f"{sum(1 for p in data['people'].values() if p.get('fit'))} of {len(data['people'])}.")


def cmd_drop(args):
    data = load(args.ledger)
    for raw in args.emails:
        email = norm_email(raw)
        if email in data["people"]:
            person = data["people"].pop(email)
            person["dropped_because"] = "dropped during review"
            data["dropped"][email] = person
            print(f"  dropped {email}")
        else:
            print(f"  not in ledger: {raw}")
    save(args.ledger, data)
    print(f"People left: {len(data['people'])}.")


def cmd_restore(args):
    data = load(args.ledger)
    for raw in args.emails:
        email = norm_email(raw)
        if email in data["dropped"]:
            person = data["dropped"].pop(email)
            person.pop("dropped_because", None)
            data["people"][email] = person
            print(f"  restored {email}")
        else:
            print(f"  not in dropped: {raw}")
    save(args.ledger, data)
    print(f"People in ledger: {len(data['people'])}.")


def cmd_show(args):
    data = load(args.ledger)
    today = date.today()
    people = sorted(data["people"].values(), key=lambda p: scoring.sort_key(p, today))
    print(f"{len(people)} people, {len(data['dropped'])} dropped. Judged: {sum(1 for p in people if p.get('fit'))}.")
    print(f"{'#':>3}  {'Name':28} {'Email':34} {'Last':10} {'Rel':8} {'Fit':8} {'Thr':>3} {'Mtg':>3} Score")
    for i, p in enumerate(people[: args.top], 1):
        last = scoring.latest(p.get("last_contact"), p.get("last_meeting"))
        print(f"{i:>3}  {(p.get('name') or '')[:28]:28} {p['email'][:34]:34} {last.isoformat() if last else '':10} "
              f"{scoring.relationship_label(p, today):8} {scoring.fit_label(p.get('fit')) if p.get('fit') else '(none)':8} "
              f"{p.get('threads', 0):>3} {p.get('meetings', 0):>3} {scoring.total_score(p, today):>5}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="People ledger for Build my Fast 50")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="add thread and event observations")
    p.add_argument("ledger")
    p.add_argument("observations")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("clean", help="drop automated senders, the client's own addresses and colleagues")
    p.add_argument("ledger")
    p.add_argument("--self", dest="self", default="", help="comma separated list of the client's own addresses")
    p.add_argument("--skip-domain", default="", help="comma separated company domains to treat as colleagues")
    p.add_argument("--keep-domain", default="", help="comma separated domains never to drop")
    p.add_argument("--no-colleague-rule", action="store_true", help="keep people at the client's own company domain")
    p.set_defaults(func=cmd_clean)

    p = sub.add_parser("judge", help="set fit, why, angle, company, title per person")
    p.add_argument("ledger")
    p.add_argument("judgments")
    p.set_defaults(func=cmd_judge)

    p = sub.add_parser("drop", help="drop people by email")
    p.add_argument("ledger")
    p.add_argument("emails", nargs="+")
    p.set_defaults(func=cmd_drop)

    p = sub.add_parser("restore", help="restore dropped people by email")
    p.add_argument("ledger")
    p.add_argument("emails", nargs="+")
    p.set_defaults(func=cmd_restore)

    p = sub.add_parser("show", help="preview the ranking")
    p.add_argument("ledger")
    p.add_argument("--top", type=int, default=25)
    p.set_defaults(func=cmd_show)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
