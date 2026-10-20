# MarcinAI plugin for Claude

Your Fast 50 is the first 50 people you talk to about your raise, and the best ones are people you already know. This plugin adds one skill to your own Claude account, Build my Fast 50. It reads your Gmail and Google Calendar from the last 24 months, folds in a LinkedIn or contacts export if you attach one, asks three questions about your investor profile, and hands back one spreadsheet ranked by how well you know each person and how well they fit. You upload that file in MarcinAI. Nothing else leaves your Claude account; nobody at M1 sees your mail, calendar or connections.

**Plans.** Works on Claude Pro, Max, Team and Enterprise. Not on the Free plan.

**Outlook.** The mail and calendar part runs on Gmail and Google Calendar. If your mail is in Outlook, export your Outlook contacts as a CSV file (Outlook, File, Open and Export, Import/Export, Export to a file, Comma Separated Values) and attach it in step 3. The skill builds your list from the export.

## 1. Install the plugin

1. Open Claude on the web or in the desktop app and sign in.
2. In the left sidebar, open **Customize**, then **Plugins**.
3. Press **Add**, then **Add marketplace**.
4. Paste this link and confirm: **https://github.com/chad-m1realcapital/marcinai-plugin**
5. The marketplace shows one plugin, **MarcinAI**. Open it and press **Add**. It now sits under **Your plugins**, switched on.
6. If M1 sent the plugin as a file instead: **Add**, then **Upload plugin**, and choose the file.

## 2. Turn on the connectors and file creation

1. Under **Customize**, open **Connectors**.
2. Find **Gmail**, press **Connect**, sign in to the Google account that holds your business mail, and grant the permissions. The button changes to **Disconnect** when it worked.
3. Find **Google Calendar** and do the same.
4. Open **Settings**, then **Capabilities**, and make sure **Code execution and file creation** is on. On a Team or Enterprise plan an Owner turns this on.

Both connectors are read-only: Claude can search and read, and cannot send, change or delete anything.

## 3. Run Build my Fast 50

1. Start a new chat.
2. Press the **+** button at the lower left of the message box, choose **Connectors**, and switch on **Gmail** and **Google Calendar** for this chat.
3. If you have a LinkedIn connections export or a contacts export, attach it with the same **+** button. (LinkedIn: Settings and Privacy, Data privacy, Get a copy of your data, Connections. Google: Google Contacts, Export. iPhone: iCloud.com, Contacts, Export vCard.) Skip this if you have none.
4. Type **/** in the message box, pick **MarcinAI: Build my Fast 50**, and send. Typing "Build my Fast 50" works too.
5. Claude asks three questions: what you are raising for, who your ideal investor is, and who it is not for. Answer them, or paste your investor profile from **My story** in MarcinAI.
6. Wait while Claude searches your mail and calendar, cleans out automated senders, ranks everyone and writes the file. A big mailbox takes a few minutes.
7. Download the file, **Fast 50 - your name - date.xlsx**. Its columns: Name, Email, Company, Title, Last contact, Relationship, Fit, Why they are a fit, Suggested angle, Source. Claude also shows the top ten and what it skipped, and puts anyone back if you ask.

## 4. Upload the file in MarcinAI

1. Sign in to MarcinAI and open **Lead generation**.
2. Press **Add contacts** and choose the file you downloaded.
3. MarcinAI reads it like any other list, finds or creates each person in your account, and ranks everyone overnight against your investor profile.
4. The next morning your list is under **Lead generation**, **Fast 50**, with your first messages waiting for your review.

## What the skill never does

It never sends, replies, drafts, labels, archives or deletes mail. It never creates, changes or declines calendar events. It never shares, uploads or emails the file or anything else; you download it from the chat yourself. It never copies the text of your emails into the file, only names, addresses, companies, titles, dates, and the one-line reason and suggested angle it writes for each person.

## If something is off

- The skill is not in the **/** menu: under **Customize**, **Plugins**, check that **MarcinAI** is switched on. A connector is not in the **+** menu: connect it first under **Customize**, **Connectors**. Claude says it cannot create files: step 2, item 4.
- Anything else: ask your CSM on the Day 1 or Day 5 call. M1 updates the plugin and you get new versions automatically.
