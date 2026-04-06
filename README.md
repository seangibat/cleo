# Cleo

A persistent AI assistant running as [Claude Code](https://docs.anthropic.com/en/docs/claude-code) inside a tmux session, with Signal messaging integration.

## Architecture

```
                    Signal
                      |
              signal-cli (JSON-RPC daemon)
                      |
              signal-queue.py (polls, writes inbox + history)
                      |
            inbox/*.json  +  history/*.jsonl
                      |
              signal-wait (inotifywait, background task)
                      |
              Claude Code (tmux session)
                      |
              signal-send (replies via JSON-RPC)
```

### Components

**Claude Code** runs in a tmux session (`cleo`), managed by `cleo-watch.sh` as a systemd service. Claude Code loads `CLAUDE.md` for operating instructions and `SOUL.md` for personality.

**signal-cli** runs as a JSON-RPC daemon (HTTP on port 8080, TCP on port 7583). It handles all Signal protocol operations.

**signal-queue.py** polls signal-cli for incoming messages every 2 seconds. Authorized messages are written to:
- `inbox/{timestamp}_{feed}.json` — trigger files that wake Claude
- `history/{feed}.jsonl` — append-only conversation log

**Bin tools** (in `bin/`):
- `check-feeds` — list feeds with unread messages
- `read-feed <feed_id> [count]` — read conversation history, mark as processed
- `signal-send <recipient>` — send a message (reads from stdin)
- `signal-react <recipient> <author> <timestamp> <emoji>` — send a reaction
- `signal-wait` — block until a new inbox file appears (inotifywait)

**cleo-watch.sh** keeps Claude Code alive:
- Creates the tmux session if missing
- Detects Claude Code via status bar parsing (looks for the `⏵` character in the tmux pane)
- Restarts Claude if it dies — never injects keystrokes into an active session

### Message flow

1. Signal message arrives via signal-cli
2. signal-queue.py writes a trigger file to `inbox/`
3. `signal-wait` (running as a Claude Code background task) detects the new file and exits
4. Claude Code receives the task completion notification
5. Claude runs `check-feeds` + `read-feed` to see the message
6. Claude decides whether to respond (silence is the default)
7. If responding, Claude pipes the message to `signal-send`
8. Claude restarts `signal-wait` to watch for the next message

### Memory

- `memory/MEMORY.md` — long-term memory index (contacts, groups, open threads)
- `memory/YYYY-MM-DD.md` — daily interaction logs
- `memory/summaries/` — distilled summaries from the dream cycle

## Setup

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- [signal-cli](https://github.com/AsamK/signal-cli) registered with a phone number
- `inotify-tools` (for `inotifywait`)
- Python 3.12+ with a venv (`requests`, `pyyaml`)
- tmux

### Installation

1. Clone the repo and set up the venv:
   ```bash
   cd ~/code/cleo
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```

2. Configure `config.yaml` with your bot number, authorized senders, and groups.

3. Start signal-cli as a JSON-RPC daemon:
   ```bash
   signal-cli -a +YOUR_NUMBER daemon --http 127.0.0.1:8080 --receive-mode manual
   ```

4. Install and enable the systemd services:
   ```bash
   cp systemd/*.service ~/.config/systemd/user/
   # Edit paths in the service files to match your setup
   systemctl --user daemon-reload
   systemctl --user enable --now signal-queue cleo-watch
   ```

5. Enable user lingering so services start at boot:
   ```bash
   sudo loginctl enable-linger $USER
   ```

### Customization

- `CLAUDE.md` — operating instructions (startup procedure, message handling, scheduled jobs)
- `SOUL.md` — personality and tone
- `config.yaml` — bot number, authorized senders/groups, signal-cli RPC URL
