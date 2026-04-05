#!/usr/bin/env bash
# cleo-watch: Keep Cleo's Claude Code tmux session alive.
#
# Checks every 30 seconds:
#   1. Session missing  → create it, start claude --continue
#   2. Claude not running (no status bar visible) → restart
#   3. Otherwise → do nothing (never send keystrokes to an active session)
#
# Detection: parse the tmux pane for Claude Code's status bar (⏵ character).
# This is reliable regardless of process tree depth or node naming.
#
# Run as a systemd service (see systemd/cleo-watch.service).

set -euo pipefail

SESSION="cleo"
WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_INTERVAL=30

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [cleo-watch] $*"
}

session_exists() {
    tmux has-session -t "$SESSION" 2>/dev/null
}

claude_running() {
    # Check if Claude Code's status bar is visible in the tmux pane.
    # The status bar contains ⏵ (U+23F5) which is unique to Claude Code.
    local pane_content
    pane_content=$(tmux capture-pane -t "$SESSION" -p 2>/dev/null) || return 1
    echo "$pane_content" | grep -q '⏵' 2>/dev/null
}

start_claude() {
    log "Starting claude --continue in session '$SESSION'"
    # Use C-c to kill any partial input, then start fresh
    tmux send-keys -t "$SESSION" C-c 2>/dev/null || true
    sleep 0.5
    tmux send-keys -t "$SESSION" "cd $WORKDIR && (claude --dangerously-skip-permissions --continue 2>/dev/null || claude --dangerously-skip-permissions)" Enter
}

while true; do
    if ! session_exists; then
        log "Session '$SESSION' not found — creating"
        tmux new-session -d -s "$SESSION" -c "$WORKDIR" -x 220 -y 50
        tmux rename-window -t "$SESSION:0" "cleo"
        sleep 1
        start_claude

    elif ! claude_running; then
        log "Claude Code not detected in pane — restarting"
        start_claude

    fi

    sleep "$CHECK_INTERVAL"
done
