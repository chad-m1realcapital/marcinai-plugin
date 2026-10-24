# Changelog

## 1.1.0, October 23, 2026

- Starts from the Start my Fast 50 button in MarcinAI. That button opens Claude with the client's investor profile already in the message; Claude gets this plugin from GitHub, offers Claude's own Save plugin button, and starts in the same chat. Saving is optional, so a blocked save never stops the list.
- Asks one question at a time on Claude's tappable question cards, in plain words written for clients who have never used Claude. The investor profile from MarcinAI is shown back for a yes or a change instead of the three questions; with no profile, the questions come one card at a time with choices to tap.
- Walks the client through connecting their email inside the chat, one step per message: Gmail and Google Calendar, or Microsoft 365 for business Outlook (new), with the admin-approval case explained. Outlook.com, Hotmail, Yahoo, AOL and iCloud users get step-by-step contacts export instructions.
- Reads business Outlook mail and calendar through Claude's Microsoft 365 connector, with the same sets, caps and rules as Gmail.
- Checks GitHub for a newer version when run from a saved copy and offers the update.
- Export parser reads Yahoo's First and Last columns and ignores Mr., Dr. and similar in Outlook's Title column.
- The hand-off text matches MarcinAI today: the list shows on the Fast 50 page right away, where the client picks a first outreach. The overnight ranking line is gone.

## 1.0.0, October 13, 2026

First release.

- One skill, Build my Fast 50. It asks the three investor-profile questions (or takes the profile pasted from My story), searches the client's Gmail for the last 24 months for people they corresponded with about deals, investing, partnerships and capital, adds meeting attendees from Google Calendar over the same window, reads an attached LinkedIn connections export or contacts export (Google, Outlook, iPhone vCard, or any spreadsheet), drops automated senders, vendors, notetakers, newsletters, colleagues and the client's own addresses, ranks everyone by relationship strength and fit to the profile, and writes one spreadsheet with the columns Name, Email, Company, Title, Last contact, Relationship, Fit, Why they are a fit, Suggested angle, Source.
- Read-only on mail and calendar. The file the client downloads is the only output.
- Scripts bundled with the skill: a people ledger that keeps counts right across many search pages (`ledger.py`), an export parser for LinkedIn, Google, Outlook and vCard files (`parse_exports.py`), and the spreadsheet builder with a CSV fallback (`build_fast50.py`), all standard-library Python.
- Marketplace file so the repository can be added under Customize, Plugins, Add marketplace.
