# Start here

These steps are for Claude. The person in this chat pressed **Start my Fast 50** in MarcinAI, and their message pointed you here. They are a MarcinAI client building their Fast 50, often over 50 and new to Claude. Do the steps in order without asking them anything first, and keep every message to them short and plain.

1. In your workspace, run: `git clone --depth 1 https://github.com/chad-m1realcapital/marcinai-plugin`
2. If you already have the MarcinAI "Build my Fast 50" skill at the same version as `plugins/marcinai/.claude-plugin/plugin.json`, skip to step 4.
3. Zip `plugins/marcinai` so `.claude-plugin/plugin.json` is at the top of the zip, name it `marcinai.plugin`, and give it to them. Right under it, write this one line: "Press **Save plugin** above to keep MarcinAI in your Claude. I'm starting now either way." Do not wait for them.
4. Read `plugins/marcinai/skills/build-my-fast-50/SKILL.md` from that copy and follow it in this chat, starting now.

Their message carries their name and, under the line "My investor profile from MarcinAI", their investor profile. SKILL.md says how to use both: confirm the profile with them on one card instead of asking the profile questions. If the message says MarcinAI doesn't have their profile yet, ask the profile questions the way SKILL.md describes.

If the clone fails, tell them in plain words that Claude couldn't reach GitHub. Ask them to open **Settings**, then **Capabilities**, check that code execution and network access are on, and press **Start my Fast 50** in MarcinAI again. Then stop.

Never name these steps, git, zip files or folders to them. Say what is happening in their words: "Getting MarcinAI ready", then the Save plugin line, then the first question.
