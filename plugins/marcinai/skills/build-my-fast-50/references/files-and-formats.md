# Files and formats

Read this when you handle an attached export (step 5), when you build the file (step 8), or when a script complains about its input.

## Where files are

- In chat on claude.ai and the desktop app, a file the client attaches lands under `/mnt/user-data/uploads/`. Save the finished spreadsheet under `/mnt/user-data/outputs/` so the chat offers it for download.
- In Cowork, attached files and outputs sit in the task's folder; save the spreadsheet where the task puts files for the person.
- The skill's scripts are in this skill's `scripts/` folder. In Claude Code and Cowork, `${CLAUDE_SKILL_DIR}/scripts/` points there. When the client started from the MarcinAI button, you cloned the plugin from GitHub and the scripts are under `marcinai-plugin/plugins/marcinai/skills/build-my-fast-50/scripts/`. Otherwise find them once with `find / -name ledger.py -path "*build-my-fast-50*" 2>/dev/null | head -1`.
- Working files (people.json, observations.json, judgments.json, exports.json) stay in the sandbox's working folder. They are not deliverables and never leave the chat.

## Export formats the parser reads

`parse_exports.py` detects each file by its header.

| Export | How the client gets it | Columns it carries |
| :- | :- | :- |
| LinkedIn connections | Settings and Privacy, Data privacy, Get a copy of your data, Connections (desktop only, arrives by email as a .zip, minutes to a day). Pass the .zip as it is or the Connections.csv inside it; from a .zip only Connections.csv is read. | `First Name, Last Name, URL, Email Address, Company, Position, Connected On`, with three note lines above the header. Email is blank for most connections; that is LinkedIn's privacy setting, not a parser miss. |
| Google Contacts | Google Contacts, Export, Google CSV | Newer files: `First Name, Last Name, Organization Name, Organization Title, E-mail 1 - Value`. Older files: `Given Name, Family Name, Organization 1 - Name, Organization 1 - Title, E-mail 1 - Value`. Both are handled. |
| Outlook | Outlook, File, Open and Export, Import/Export, Export to a file, Comma Separated Values | `First Name, Last Name, Company, Job Title, E-mail Address` |
| Outlook.com and Outlook on the web | People, Manage contacts, Export contacts, All contacts, Export | The same Outlook columns. Its `Title` column holds Mr., Dr. and the like; the parser ignores those. |
| Yahoo | Yahoo Mail, Contacts, the three dots, Export to CSV file | `First, Last, Email, Title, Company` among others |
| AOL | AOL Mail, Contacts, More, Export | A CSV with name and email columns |
| iPhone through iCloud | icloud.com/contacts, the actions button, Select All Contacts, the share button, Export vCard | A `.vcf` file with `FN`, `N`, `EMAIL`, `ORG`, `TITLE` |
| Any spreadsheet | | Any CSV with a column that looks like a name and one that looks like an email |

Excel files (`.xlsx`) from the client: convert to CSV first (`python3 -c "import openpyxl, csv, sys; ..."`, or ask the client to save as CSV) and then run the parser.

The parser prints how many people each file gave and how many look High or Medium fit from their title or company. Pass the client's own words with `--keywords` (asset class, market, deal names) so those count toward Medium.

## The ledger (people.json)

Written and read by `ledger.py`. One entry per email address under `people`, with dropped people kept under `dropped` so they can be restored.

```json
{"people": {
  "jane@doecapital.com": {
    "email": "jane@doecapital.com", "name": "Jane Doe", "company": "Doe Capital", "title": "Managing Partner",
    "first_contact": "2025-11-03", "last_contact": "2026-08-14", "last_meeting": "2026-06-02",
    "threads": 6, "they_wrote": 5, "you_wrote": 4, "meetings": 2,
    "topics": ["LP returns on Oak Street", "Coffee with Jane"], "sources": ["Mail", "Calendar"],
    "fit": "High", "why_fit": "...", "angle": "...",
    "seen": {"threads": ["18f3a...", "18f2b..."], "events": ["evt1", "evt2"]}}},
 "dropped": {}, "meta": {"updated": "2026-10-13"}}
```

`threads` counts separate threads; `they_wrote` counts threads where the person sent something; `you_wrote` counts threads where the client sent something; `meetings` counts calendar events. The `seen` lists are what make re-adding a page harmless.

## Observations (observations.json)

A JSON array; any mix of threads and events. See `search-playbook.md` for the fields. Re-running `ledger.py add` with the same file changes nothing.

## Judgments (judgments.json)

A JSON array. Only the keys you give are changed.

```json
{"email": "jane@doecapital.com", "fit": "High", "why_fit": "...", "angle": "...", "company": "...", "title": "...", "name": "..."}
{"email": "bot@notetaker.example", "drop": true, "reason": "notetaker bot"}
{"name": "Raj Patel", "fit": "Medium", "why_fit": "...", "angle": "..."}
```

`ledger.py judge` matches by email, then by exact name for ledger people. `build_fast50.py --judgments` matches the same way across ledger and export rows, which is how export-only people without an email get judged.

## The output file

Name: `Fast 50 - <client's first name or company> - <YYYY-MM-DD>.xlsx`. The builder falls back to `.csv` with the same header when the spreadsheet library is missing; MarcinAI's importer takes either.

One sheet, called Fast 50, bold header row, frozen, filterable. Exactly these columns in this order:

| Column | What goes in it |
| :- | :- |
| Name | First and last name as the person writes it. Blank only when nothing but an address was ever seen. |
| Email | Lowercase. Blank for LinkedIn connections who hide theirs. |
| Company | From a signature, the export, or an obvious business domain (doecapital.com reads as Doe Capital). Blank when unknown; never guessed. |
| Title | From a signature or the export. Blank when unknown; never guessed. |
| Last contact | YYYY-MM-DD, the most recent of the last email and the last meeting. For export-only people, the LinkedIn connection date when there is one, otherwise blank. |
| Relationship | Strong, Warm, Dormant or Thin. |
| Fit | High, Medium, Low or Unknown. |
| Why they are a fit | One line, evidence first. |
| Suggested angle | One line, the first move. |
| Source | Mail, Calendar, LinkedIn export, Google export, Outlook export, Phone export, Contacts export, joined with " + " when several. |

Everyone who survived cleaning is in the file, best first; the top of the list is the Fast 50. No message text, no subjects, no URLs, no phone numbers, no notes about anyone beyond the two lines.

## The chat summary, after the file

Keep it short, plain, and name no email contents. The client may be new to all of this, so no jargon and no numbers they did not need. The shape:

- "Your list is ready: 184 people. 131 came from your email, 44 from your calendar, and 38 from your LinkedIn file."
- "The top ten:" then ten lines, each a name with a few plain words, for example "Jane Doe, you know her well, strong fit".
- "I left out 212 automated senders and 9 people at your own company. Tell me if you want any of them back."
- When a cap was hit: "Your mailbox is big, so I read the most relevant two years of deal and investor email."

Then the upload steps from step 9 of SKILL.md, word for word or close to it.
