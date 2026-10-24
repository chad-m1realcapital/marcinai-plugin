# MarcinAI plugin for Claude

Your Fast 50 is the first 50 people you talk to about your raise, and the best ones are people you already know. This plugin adds one skill to your own Claude account, Build my Fast 50. It reads your Gmail and Google Calendar, or your business Outlook, from the last 24 months, folds in a LinkedIn or contacts file if you have one, and hands back one spreadsheet ranked by how well you know each person and how well they fit your investor profile. You upload that file in MarcinAI. Nothing else leaves your Claude account; nobody at M1 sees your mail, calendar or connections.

**Plans.** Works on Claude Pro, Max, Team and Enterprise. Not on the Free plan.

## The easy way: start from MarcinAI

1. In MarcinAI, press **Start my Fast 50**. It's on Getting started and on the Fast 50 page.
2. Claude opens with your message already written. Claude shows a "Use caution" note on any message that comes from a link; that's normal. Press the orange arrow to send it.
3. Claude gets the MarcinAI plugin and shows it with a **Save plugin** button. Press it once. From then on it's in your Claude.
4. Claude asks you a few questions, one at a time, and helps you connect your email if it isn't connected yet.
5. When your list is ready, download it and upload it in MarcinAI with **Add contacts**.

Each time you press **Start my Fast 50**, Claude uses the newest version of the plugin.

## Your email

- **Gmail or Google Workspace:** Claude connects to Gmail and Google Calendar. Both are read-only.
- **Outlook through your business (Microsoft 365):** Claude connects to Microsoft 365, also read-only. Your company's Microsoft account owner approves Claude once; at a small firm that's usually you.
- **Outlook.com, Hotmail, Yahoo, AOL or iCloud:** these can't connect to Claude. Claude walks you through exporting your contacts and builds the list from that file.
- **LinkedIn:** there's no LinkedIn connection. You can download your connections from LinkedIn and attach the file, or upload it in MarcinAI later.

## Installing it by hand instead

If you'd rather add it from Claude's menus:

1. Open Claude on the web or in the desktop app and sign in.
2. In the left sidebar, open **Customize**, then **Plugins**.
3. Press **Add**, then **Add marketplace**, then **Add from a repository**.
4. Paste this link and press **Sync**: **https://github.com/chad-m1realcapital/marcinai-plugin**
5. **MarcinAI** appears under **Your plugins**; search "MarcinAI" if you don't see it. Open it and press **Add**.
6. Start a new chat and type **Build my Fast 50**.

## What you get

One file, **Fast 50 - your name - date.xlsx**, with these columns: Name, Email, Company, Title, Last contact, Relationship, Fit, Why they are a fit, Suggested angle, Source. In MarcinAI, press **Add contacts** and pick the file. Your list shows on the Fast 50 page right away. There you pick your first outreach, a webinar invite or your offer, and approve the words once.

## What the skill never does

It never sends, replies, drafts, labels, archives or deletes mail. It never creates, changes or declines calendar events. It never shares, uploads or emails the file or anything else; you download it from the chat yourself. It never copies the text of your emails into the file, only names, addresses, companies, titles, dates, and the one-line reason and suggested angle it writes for each person.

## If something is off

- Claude says it can't create files: open **Settings**, then **Capabilities**, and turn on **Code execution and file creation**. On a Team or Enterprise plan an Owner turns this on.
- Anything else: ask your client success manager. They're under **Get help** in MarcinAI.
