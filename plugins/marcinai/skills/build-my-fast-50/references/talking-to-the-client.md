# Talking to the client: every card and every step

Read this before your first message. It holds the exact cards to show and the exact steps to give, so a client who has never used Claude can follow along without guessing.

The rules from SKILL.md, once more: one question per card, two to four choices, the most likely first, no "Other" choice (the card already lets them type). One step per message. Plain words. Wait for their answer before the next step.

If you have no multiple-choice card tool, ask the same question in one short line and list the choices on separate lines, numbered, so they can reply with a number.

## Card 0: the email that is already connected

Show this when mail tools are already in the chat, so you never read the wrong mailbox.

- Question: "Your email is already connected to Claude. Is it the email you use for business?"
- Choices:
  - "Yes, that's my business email"
  - "No, my business email is somewhere else"

"No": go to Card 1 and connect the right one.

## Card 1: where their email lives

Show this when no mail tools are in the chat, or after "No" on Card 0.

- Question: "Where is your business email?"
- Choices:
  - "Gmail" (also means Google Workspace: a company address that opens in Gmail)
  - "Outlook through my business" (Microsoft 365 at work)
  - "Outlook.com, Hotmail, Yahoo, AOL or iCloud"
  - "Not sure"

"Not sure": ask with one card, "When you read your business email on your computer, what does it say at the top of the screen?" Choices: "Gmail" / "Outlook" / "Neither". Gmail means Path A. Outlook means Path B, unless their address ends in outlook.com, hotmail.com, live.com or msn.com, which means Path C. Neither means Path C; if they use Apple Mail or another app, ask them to type the part of their email address after the @, and yahoo.com, aol.com, icloud.com and me.com also mean Path C.

## Path A: Gmail

If you have a tool that puts a Connect button for a connector right in the chat, use it for Gmail, then for Google Calendar, and skip the typed steps.

Otherwise, one message at a time:

1. "Click this link. It opens Claude's list of connections in a new tab: https://claude.ai/customize/connectors. Keep this chat open."
2. "Find **Gmail** and press **Connect**. Sign in with the Google account you use for business, then press **Allow**. When it worked, the button says Disconnect."
3. "Now do the same for **Google Calendar** on that page."
4. "Come back to this tab." Then the card below.

Card: "Did Gmail and Google Calendar connect?"
- "Yes, both are connected"
- "It didn't work"
- "Skip it, use a contacts file instead"

"Yes": check for the Gmail and Calendar tools. If they are not here yet, one more step: "Press the **+** button at the lower left of the message box, choose **Connectors**, and switch on **Gmail** and **Google Calendar**." Then check again.

"It didn't work": ask, with a card, what they saw ("Google said I can't sign in" / "I couldn't find Gmail on the page"); they can type anything else. A company Google account can block outside apps; if that is it, say so plainly and move them to the contacts export (Path C, Google Contacts). Claude's Gmail connector needs a paid Claude plan; on a Team or Enterprise plan the company's Claude owner adds it for the company first.

## Path B: Outlook through their business (Microsoft 365)

If you have a tool that puts a Connect button for a connector right in the chat, use it for Microsoft 365 and skip the typed steps.

Otherwise, one message at a time:

1. "Click this link. It opens Claude's list of connections in a new tab: https://claude.ai/customize/connectors. Keep this chat open."
2. "Find **Microsoft 365** and press **Connect**. Sign in with your work email and password, then press **Accept**."
3. "Come back to this tab." Then the card below.

Card: "Did Microsoft 365 connect?"
- "Yes, it's connected"
- "It says an administrator has to approve it"
- "It didn't work"
- "Skip it, use a contacts file instead"

"It didn't work": ask, with a card, what they saw ("I couldn't find Microsoft 365 on the page" / "Microsoft wouldn't let me sign in"); they can type anything else. On a Team or Enterprise Claude plan, Microsoft 365 only shows on that page after the company's Claude owner adds it. A sign-in Microsoft refuses usually means a company rule; offer the contacts file (Path C) so they are not stuck.

Microsoft's approval screen lists everything the Microsoft 365 connection can do, including sending. If they ask, say: "That list is everything Claude could be allowed to do. MarcinAI only reads your email and calendar. It never sends, changes or deletes anything."

"Yes": check for the Outlook email and calendar tools. If they are not here, give the + button step from Path A with **Microsoft 365** instead.

"An administrator has to approve it": say, in plain words, "Microsoft lets your company's account owner decide which apps can read work email. The owner approves Claude once, and then it works for everyone at your company." Then the card:
- "I'm the owner, show me how" (Recommended when the business is small)
- "Someone else runs it, I'll send them the steps"
- "Use a contacts file for now"

First offer the contacts file (Path C, Outlook on the web) so they are not stuck waiting. Then, for the owner: Microsoft calls them the Global Administrator. If that is the client, they press Connect again while signed in as that administrator, and Microsoft shows a box to approve it for the organization; tick it and accept. For someone else, or if it still fails: "Forward this link to whoever set up your company email. It has the steps for them: https://support.claude.com/en/articles/12542951"

Personal Outlook.com, Hotmail, Live and MSN accounts cannot connect. They go to Path C.

## Path C: a contacts file instead

Ask which service, with a card: "Where are your contacts?" with up to four services that fit what they told you (Outlook; Google Contacts; Yahoo; AOL; iPhone, through iCloud). Then the steps for that one, one message at a time. Tell them to do this on a computer.

- **Outlook, any kind:** do it in the browser, whatever Outlook they use day to day. Work email: https://outlook.office.com. Outlook.com, Hotmail, Live or MSN: https://outlook.live.com. Sign in, select the **People** icon in the side panel, then on the toolbar choose **Manage contacts**, then **Export contacts**, pick **All contacts**, press **Export**. The file lands in Downloads.
- **Google Contacts:** open https://contacts.google.com, tick the box next to any contact, use the **Selection actions** box at the top left and choose **All**, then press **More actions** (the three dots at the top right), choose **Export**, pick **Google CSV**, and press **Export**.
- **Yahoo:** in Yahoo Mail, open **Contacts**, press the three dots (**More**), choose **Export to CSV file**. If Yahoo refuses, a contact with unusual characters in the name is usually the cause.
- **AOL:** in AOL Mail, open **Contacts**, choose **More**, then **Export**. AOL's help page: https://help.aol.com/articles/add-edit-or-delete-contacts-in-aol-mail
- **iPhone, through iCloud:** open https://www.icloud.com/contacts on a computer and sign in, press the actions button at the top of the list and choose **Select All Contacts**, then the share button, then **Export vCard**.

Then: "Now come back here, press the **+** button at the lower left of the message box, choose to add a file, and pick the file you just downloaded." Wait for the file.

When this is the only source, say once: "This list is built from your contacts, not your email, so I can rank people by who they are but not by how recently you talked."

## Card 2: LinkedIn

Offer once, right after the profile is settled, whether or not their email is connected.

- Question: "Want to add your LinkedIn connections too?"
- Choices:
  - "I have my LinkedIn file, I'll attach it" (LinkedIn's .zip, or the Connections.csv inside it, both work)
  - "Not now"
  - "Show me how to get it"

"Show me how": on a computer, on LinkedIn press **Me** (their photo, top right), then **Settings & Privacy**, **Data privacy**, **Get a copy of your data**, pick **Connections** (or the larger archive if Connections is not offered), press **Request archive**. LinkedIn emails a link when the file is ready, which can take from a few minutes to a day. The file is a .zip. Then say: "We don't need to wait. I'll build your list from your email now. When LinkedIn's email arrives, double-click the zip file to open it, and upload the file inside called Connections.csv in MarcinAI with Add contacts."

## Card 3: confirm the profile from MarcinAI

When the opening message carried "My investor profile from MarcinAI", the short version goes inside the question, because the card is what the client reads:

- Question: "MarcinAI has you raising about $3M for one apartment deal, starting with your past investors, dentists near you and business owners who sold a company. Is that still right?"
- Choices:
  - "Yes, that's right"
  - "Change something"

"Change something": ask them to type what is different, take it as the update, and do not ask again.

## Cards 4 to 8: the profile questions, when MarcinAI sent none

One card each, in this order. Build the choices from anything they already told you.

4. "What are you raising for right now?" - "A deal I'm buying" / "A fund" / "Both" / "Not sure yet"
5. "What kind of property?" (multiple choice allowed) - "Apartments" / "Self storage" / "Industrial" / "Retail or office". They can type anything else. If they mention a market, keep it.
6. "About how much are you raising?" - "Under $1 million" / "$1 to $5 million" / "$5 to $20 million" / "More than $20 million"
7. "Who are your best investors?" (multiple choice allowed) - "People who've invested with me before" / "Doctors and other high earners" / "Business owners" / "Friends and family"
8. "Who is this not for?" (multiple choice allowed) - "People who aren't accredited" / "People who need their money back soon" / "Nobody, keep everyone"

Then Card 2 (LinkedIn), then the one line from step 2 of SKILL.md, and start the sweep.

## While you work

One line before the sweep, and at most one short line every few minutes after that. Examples:

- "Reading your email from the last two years. On a busy inbox this takes a while, so keep this tab open."
- "Halfway there. I've found about 120 people so far."
- "Now your calendar."
- "Ranking everyone against your investor profile. Almost done."

Never name a search query, a tool or a file you are writing.
