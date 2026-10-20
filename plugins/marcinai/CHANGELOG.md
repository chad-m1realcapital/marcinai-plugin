# Changelog

## 1.0.0, October 13, 2026

First release.

- One skill, Build my Fast 50. It asks the three investor-profile questions (or takes the profile pasted from My story), searches the client's Gmail for the last 24 months for people they corresponded with about deals, investing, partnerships and capital, adds meeting attendees from Google Calendar over the same window, reads an attached LinkedIn connections export or contacts export (Google, Outlook, iPhone vCard, or any spreadsheet), drops automated senders, vendors, notetakers, newsletters, colleagues and the client's own addresses, ranks everyone by relationship strength and fit to the profile, and writes one spreadsheet with the columns Name, Email, Company, Title, Last contact, Relationship, Fit, Why they are a fit, Suggested angle, Source.
- Read-only on mail and calendar. The file the client downloads is the only output.
- Scripts bundled with the skill: a people ledger that keeps counts right across many search pages (`ledger.py`), an export parser for LinkedIn, Google, Outlook and vCard files (`parse_exports.py`), and the spreadsheet builder with a CSV fallback (`build_fast50.py`), all standard-library Python.
- Marketplace file so the repository can be added under Customize, Plugins, Add marketplace.
