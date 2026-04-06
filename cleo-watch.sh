#!/usr/bin/env bash
# cleo-watch: Keep Cleo's Claude Code tmux session alive.
#
# Checks every 30 seconds:
#   1. Session missing  → create it, start claude --continue
#   2. Claude not running (no status bar visible) → restart
#   3. Otherwise → do nothing (never send keystrokes to an active session)
#
# Run as a systemd service (see systemd/cleo-watch.service).

set -euo pipefail

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

SESSION="cleo"
WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_INTERVAL=30
# Require multiple consecutive failures before restarting (debounce)
FAIL_THRESHOLD=3
fail_count=0

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [cleo-watch] $*"
}

session_exists() {
    tmux has-session -t "$SESSION" 2>/dev/null
}

claude_running() {
    # Check if Claude Code is running by looking for its process in the pane's
    # process tree, OR for the status bar character in the pane content.
    # Belt and suspenders — either signal means Claude is alive.
    local pane_pid
    pane_pid=$(tmux display-message -t "$SESSION:0.0" -p "#{pane_pid}" 2>/dev/null) || return 1

    # Method 1: process check (look for claude/node anywhere in process group)
    if pgrep -g "$(ps -o pgid= -p "$pane_pid" 2>/dev/null | tr -d ' ')" -f "node.*claude" >/dev/null 2>&1; then
        return 0
    fi

    # Method 2: status bar check (locale-safe — use hex match for ⏵ U+23F5)
    local pane_content
    pane_content=$(tmux capture-pane -t "$SESSION:0.0" -p 2>/dev/null) || return 1
    if echo "$pane_content" | grep -qP '\xe2\x8f\xb5' 2>/dev/null; then
        return 0
    fi
    # Fallback: try plain grep in case locale is fine
    if echo "$pane_content" | grep -q '⏵' 2>/dev/null; then
        return 0
    fi

    return 1
}

start_claude() {
    log "Starting claude --continue in session '$SESSION'"
    # Use C-c to kill any partial input, then start fresh
    tmux send-keys -t "$SESSION:0.0" C-c 2>/dev/null || true
    sleep 0.5
    tmux send-keys -t "$SESSION:0.0" "cd $WORKDIR && (claude --dangerously-skip-permissions --continue 2>/dev/null || claude --dangerously-skip-permissions)" Enter
}

while true; do
    if ! session_exists; then
        log "Session '$SESSION' not found — creating"
        tmux new-session -d -s "$SESSION" -c "$WORKDIR" -x 220 -y 50
        tmux rename-window -t "$SESSION:0" "cleo"
        sleep 1
        fail_count=0
        start_claude

    elif ! claude_running; then
        fail_count=$((fail_count + 1))
        if (( fail_count >= FAIL_THRESHOLD )); then
            log "Claude Code not detected ($fail_count consecutive checks) — restarting"
            start_claude
            fail_count=0
        else
            log "Claude detection failed ($fail_count/$FAIL_THRESHOLD) — waiting"
        fi

    else
        fail_count=0
    fi

    sleep "$CHECK_INTERVAL"
done
