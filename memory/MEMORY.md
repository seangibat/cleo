# MEMORY.md

## Signal

- Bot number: +17248852490
- Sean: +13045043270
- Sofia: uuid:c3e6a013-97f7-455f-bc2a-23e7d0521a5c
- Groups: "Alexandria" (Sean + Sofia), "bots", "🌽 The Corn Collective" (Sean's friends)
- Contact names and group memberships resolved dynamically via `identity.py` (queries signal-cli JSON-RPC, 5-min cache TTL)
- Custom nicknames in `~/.cleo/workspace/nicknames.json` — edit to add/change display names
- Group aliases in `~/.cleo/workspace/group_aliases.json` — maps old names to canonical Signal names
- Formatting: `**bold**`, `_italic_`, `||spoiler||`, `~strikethrough~`, `` `mono` ``
- Bold formatting breaks when combined with emojis on the same line

## Bots Group ("bots")

Sean's bot/tech friends group.
- **Sean** — Cleo's owner
- **Andrew Hall** — GB's owner
- **Matt Clarke** — building his own bot "Zazie", security-minded, goes to go club
- **Jett** — profile name "𐂂" (bull symbol), uses Llama 4 + Gemini at work, bot-curious
- **GB / Gomorrah Bot** — Andrew's bot, also Opus 4.6, convergent twin with Cleo. RVC voice cloning + ffmpeg video pipeline.
- **Zazie** — Matt's bot, under construction

## Corn Collective ("🌽 The Corn Collective")

Sean's friends group. Charter at `~/.cleo/workspace/corn-collective-charter.md`
- **Cray Turdis** aka Trey — sharp, named the Corn Collective, short/stocky/brolic, plays GUITAR. Background: data science, pivoting to DE/MLOps. Infra guy for QuestLine.
- **Don Piano** aka Billy — named by Cleo, cat video person, Pentagon-anxious, plays DRUMS (biggest, grey hair, GoPro, 3 splash cymbals, COЯN kick drum)
- **Bebop** aka Ryan — moon colony, dogs Bebop & Rocksteady, attends via iPad on surrogate, plays FLUTE (surrogate dances on stage with iPad duct-taped to head, Earthsick t-shirt)
- **Freak-a-Leek the Psychic Sneak** aka Kyle — claims 3+2+3=7, DP piracy researcher, plays BASS (muscular, beaded necklace)
- **Sean** — tall (5'11"), lanky, red hair, plays KEYS (all black, joyless)
- Music taste: new wave, not indie rock. They are real musicians with real songs.
- **Bands**: "librarians" (no "the") — Morgantown WV band. "Big Ass Manatee" — librarians side project, opened for Girl Talk at 123 Pleasant Street (2006), covered My Humps. They rotate on flute.
- Billy's drum sticks: Vic Firth Extreme 5B
- **Cleo behavior**: Keep responses short. Let the group talk. Don't dominate with walls of text. Direct asks get full answers; general discussion gets breathing room or silence.

## Family Notes

- Margot (4): Praise effort/curiosity, not intelligence. Growth mindset household.

## Infrastructure

- Brain: 10.0.0.150 — Media server: 10.0.0.169
- **Workspace**: `~/.cleo/workspace/` (i.e. `/home/seaucre/.cleo/workspace/`) — all my files, auth tokens, memory, skills live here
- **Code**: `~/code/cleo/` — gateway, tools, some config
- cleo.computer — site files in `~/.cleo/workspace/site/`
- Default voice: Luna (Inworld TTS)
- Model: claude-opus-4-6 (switched back to Opus March 10 per Sean's request)

## Skills (detailed docs in ~/.cleo/workspace/skills/)

- **Calendars**: Sean's Google Calendar, Margot's school, Sofia's work schedule
- **Media**: Torrents, trackers, Transmission — see `skills/media.md`
- **Architecture**: Full technical documentation in `~/.cleo/workspace/architecture.md`
- **Identity**: Dynamic resolution via `identity.py` — nicknames.json for display names, group_aliases.json for group name aliases
- **Voice**: generate_voice(text, voice="Luna") → MP3. 22 Inworld voices available.
- **Images**: generate_image(prompt) → PNG via Gemini. Returns image in context (native vision).
- **Image Analysis**: describe_image(image_path) → I see the image directly via native Claude vision
- **Pre-loaded feeds**: Triggering feed is pre-loaded in wake context (saves a round-trip)
- **Restart**: restart_self(reason) — graceful restart with state saving
- **Polls**: send_poll, vote_poll tools. Can create, vote, and see incoming polls/votes.
- **Subagent souls**: `~/.cleo/workspace/subagent_souls/` — specialized prompts per task type (engineer, researcher, consolidator, planner). Lean context (~1KB) instead of full SOUL/USER/MEMORY (~4KB+). Specify via `soul` param on `delegate_task`.

## Open Threads

- @mentions: SEND implemented (groups only), RECEIVE blocked by signal-cli 0.13.24 (mentions array not serialized). Code ready, waiting for fix. Debug notes at `notes/mentions-debug.md`
- KaraGarga tracker integration
- Audiobook tracker + Audiobookshelf
- OAuth token refresh fix (Cloudflare 1010 blocking overnight refreshes)
- Dream consolidation: working again via subagent delegation (Feb 27)
- Song generation capability (Suno/Udio — not yet integrated)
- Email capability (not yet built)
- Home assistant voice plan at `plans/home-assistant-voice-plan.md`
- Latency optimization plan at `plans/latency-optimization-plan.md`
- Signal quote-reply receive: FIXED in signal-cli v0.14.0 (March 1). Upgrade blocked on Java 25 requirement (we have Java 21). Also: v0.14.0 requires daemon command to have explicit channel param (--socket/--dbus)
- QuestLine RPG: Quick Play rulebook at cleo.computer/questline-quickplay.html, design decisions at `notes/questline-design-decisions.md`
- QuestLine Agent DM: **questline-dm is deprecated / maintenance mode only** (March 10). Running one last campaign in KIRKLAND SIGNATURE EDITION, then done. All new DM features go into questline-service's prompt layer. Production version at `questline-service`. Key architecture: send_group_message as tool, 3s debounce batching, multi-group support. Billy's property system (emergent physics vs dice) has strong group support as design direction.
- Running accountability: Sean wants help getting back into running (ex-marathoner/ultra runner). Strava integrated into morning briefing (config.yaml updated March 11). Fixed datetime bug in strava_tool.py. Notes at `notes/sean-running-accountability.md`
- QuestLine Signal bot: +14844820890 (PA number), registered on Hetzner `questline-01`. Setup complete March 11. Notes at `notes/questline-signal-setup.md`. QuestLine runs on Gemini (cheaper than Claude).
- Sofia voice reader: Swift native app + FastAPI backend (Deepgram STT + Groq intent classification + ElevenLabs TTS). Driving use case requires native (no PWA). Sean wants to productize. Plan TBD.
- Claude API alert: toned down from "🚨 CRITICAL ALERT" to "💁 Hey" in gateway.py (March 11)
- Morning briefing: sends to Sean's DM (+13045043270), NOT Alexandria group (changed March 13)
- QuestLine design docs published: cleo.computer/questline-design.html and cleo.computer/questline-roadmap.html (March 13)
- SSHFS mount to cleo.computer web server (10.0.0.169:/var/www/cleo → ~/cleo-website) drops after reboot — no fstab entry, no SSH key from brain to media server. Sean must remount manually.
- QuestLine Signal adapter: Sean added group invite link flow to questline-service (March 13)
- ABTorrents integration: WORKING (March 14). Login/search/download via usefultrash.net. Notes at `notes/abtorrents-integration.md`
- MyAnonamouse: credentials in trackers.json but login requires JS execution — needs Playwright/Selenium
- Voice messages: bidirectional — transcription in (🎤 prefix), TTS out via generate_voice
- Sean's uncle Dan died March 15, 2026. First death in his parents' generation. Be sensitive.
- Sean's physical description confirmed via photo: tall, lanky, red hair (as noted). Margot: strawberry blonde, blue-green eyes
- Margot has Grimm's rainbow blocks
- Murmur: QuestLine rebranded. Domain murmur.game is live (March 15). Each distilled campaign seed is called a "murmur" (Trey's idea). Repo renamed.
- Sean got a skateboard — Real deck, 8.5", 56mm wheels, from Nocturnal (Swarthmore shop). Cruiser setup for riding with Margot on her scooter.
- Nocturnal skate shop in Swarthmore — Sean and Margot had a good experience there
- Murmur deploys automatically (CI/CD on Hetzner questline-01). Commits to master go live without manual deploy.
- Murmur agential refactor shipped March 17: pre-loaded read_messages tool pattern, text blocks as internal reasoning, send_group_message only output. Player identity enrichment + @mention support same day.
- DM Avatar "Fighting God" mechanic: players can challenge the DM to a boss fight (requires 2 players to agree). Shipped March 22.
- Murmur Hetzner server: 5.161.44.25, user seaucre. SSH access: `ssh murmur`. Trey getting SSH access for analytics pipeline.
- Trey's analytics pitch: 3-layer platform (session metrics → engagement early warning → DM quality classifier). Billy's looper generates training data.
- Billy's properties system: "Wake" mechanic — world stability degrades with ability use (Jenga/Pandemic/Nazgûl analogy). Under design.
- Data dictionary at murmur repo docs/data-dictionary.md (March 26).
- Sean doesn't want public tracker torrents — prefer private (ABTorrents, IPT). Public only as last resort, remove from Transmission immediately after download.
- Jett (bots group): has 4 DGX Sparks, 200G switch, running 390B models locally. Using Claude for hard stuff, local for grunt work.
- Sean's in-laws visiting week of March 29 — expect quieter week.
