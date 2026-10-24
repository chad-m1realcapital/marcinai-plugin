# Ranking, fit, and the two lines per person

Read this at step 7 of SKILL.md. The scripts compute relationship strength from the counts in the ledger; you judge fit against the investor profile and write the "why" and the "angle". This file says how both work so the file reads the same way every time.

## Why relationship weighs more than fit

Marcin's Fast 50 is the first 50 conversations, and the first wave goes to the warm network as a reconnection, not a pitch. Dormant contacts and connectors come next, and cold names last. So a person the client has a real history with ranks above a stranger with a perfect title. Fit then decides the order inside each band and keeps people who do not fit the profile near the bottom.

Score = relationship points (0 to 60) + fit points (0 to 40). Highest first, then the most recent contact, then the name.

## Relationship points (computed by the scripts)

| Signal | Points | Why it counts |
| :- | :- | :- |
| Last contact under 3 months ago | 20 | A live conversation |
| 3 to 6 months | 16 | |
| 6 to 12 months | 12 | |
| 12 to 18 months | 7 | |
| 18 to 24 months | 3 | |
| Two-way: they wrote and the client wrote | 15 | The difference between a relationship and an inbox |
| Only they wrote | 5 | |
| Only the client wrote | 3 | |
| 9 or more threads | 12 | Frequency |
| 4 to 8 threads | 8 | |
| 2 to 3 threads | 4 | |
| 4 or more meetings | 13 | Calendar time is the strongest single signal |
| 2 to 3 meetings | 9 | |
| 1 meeting | 6 | |

Labels, in this order of checks:

- **Dormant**: a real past relationship (two-way mail or at least one meeting) whose last contact is 12 or more months ago. Checked first because a dormant relationship is its own move: reconnect, do not pitch.
- **Strong**: two-way or met, 40 points or more.
- **Warm**: two-way or met, 22 to 39 points.
- **Thin**: everything else. One inbound email with no reply is Thin however recent it is, and a Thin contact keeps at most 10 relationship points in the total, so recency alone cannot carry a stranger up the list.

## Fit (judged by you)

Judge each person against the profile from step 2: what the client is raising for, who the ideal investor is, who it is not for. Use what the threads and meetings showed, the title and company, and the past-investor signal.

- **High** (40 points): evidence they invest or deploy capital (an LP, wrote a check, asked about returns or terms, runs a fund or family office, a capital or equity partner, a co-GP), or they match the ideal investor closely (the profession, the means, the stated interest), or they have invested with the client before. Past investors are always High.
- **Medium** (25 points): plausible. A senior professional, a business owner, someone industry adjacent, someone who asked about the business once, or a connector with reach into the people the client wants (brokers, attorneys, CPAs, wealth advisors, community leaders).
- **Low** (0 points, and relationship points halved): a real contact who does not fit, including anyone the "not for" answer rules out, and service providers the filter kept (a contractor, a title rep). Say why in the "why" line so the client sees the decision. Low fit people stay in the file, at the bottom.
- **Unknown** (12 points): not enough to judge. Use it rather than guessing.

Judge the people with mail or calendar history yourself, every one of them; that is the point of the plugin. Export-only people get a first pass from `parse_exports.py` (the title and company), and you confirm or change the ones near the top. People from the export whose title says nothing stay out of the file unless the client asks for all of them (`--all-exports`); the export itself can go into MarcinAI directly.

## The "why they are a fit" line

One line, 8 to 25 words, evidence first, dated when you can. Name the signal, not the adjective.

- "LP in Oak Street; asked about Q2 returns in August 2026; coffee in June."
- "Runs a family office; discussed a capital partnership in February 2025; quiet since."
- "Anesthesiologist and practice owner, the high income professional in your profile; two threads about 1031 timing."
- "Commercial broker in Dallas who sent you the Elm Street deal; knows the owners who sell."
- "Your attorney on the last two closings; a connector to clients with money, not an investor."
- "General contractor on the Maple job; a vendor relationship, not an investor." (Low)
- "LinkedIn connection since 2024; title reads Managing Partner at a capital firm; no mail history." (export only)

Never quote email text. Never include numbers the client did not state (no invented check sizes). If the evidence is thin, say so plainly: "One exchange in March 2026 about the market; fit unclear."

## The "suggested angle" line

One line, the specific first move, matched to the relationship and the fit. The client sends nothing from this file; the line is a suggestion they will see in MarcinAI next to the name.

| Relationship | Fit | The move |
| :- | :- | :- |
| Strong | High | Direct: share the current deal or fund and ask for a call this week. Reference the last thing you discussed. |
| Warm | High | Reconnect with one specific reference to your last exchange, then ask for 20 minutes to walk through the raise. |
| Dormant | High | Reconnection only, no pitch: a short personal note on what changed since you last spoke, and an invitation to catch up. |
| Thin | High | Warm it first: a value-first note (a market update, a congratulation on something real) or an introduction through a mutual contact. |
| Any | Medium | Catch up, one line on what you are building, then ask who in their circle invests in deals like yours. |
| Any | Connector (a Medium or High who knows the right people) | Ask for two introductions to people who invest in what you do, and offer something back. |
| Any | Past investor | Thank them, update them on performance, ask for a re-up and a referral. |
| Any | Low | Hold for a later wave; a general update when there is news to share. |

Make the line personal where the history allows it: "Mention the Elm Street deal she sent you and ask what she is seeing in Dallas this quarter" beats "Reconnect and ask for a call."

## Judging in batches

Write judgments as a JSON array of 20 to 30 people at a time and run `ledger.py judge people.json judgments.json` after each batch. The ledger reports how many are judged so far. Export-only people are judged through `build_fast50.py --judgments`, matched by email or by exact name.

```json
[
 {"email": "jane@doecapital.com", "fit": "High",
  "why_fit": "LP in Oak Street; asked about Q2 returns in August 2026; coffee in June.",
  "angle": "Share the Dallas deal and ask for a 20 minute call this week, picking up from the returns conversation.",
  "company": "Doe Capital", "title": "Managing Partner"},
 {"email": "carl@carlbuilds.com", "drop": true, "reason": "general contractor, vendor only"}
]
```
