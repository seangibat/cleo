#!/usr/bin/env bash
# cleo-start: Start Cleo's tmux session from scratch.
# Kills any existing session and creates a fresh one.
# For day-to-day use, cleo-watch handles restarts automatically.
#
# Usage: ./cleo-start.sh [--fresh]
#   --fresh  also delete inbox/.processed so all history is treated as unread

set -euo pipefail

SESSION="cleo"
WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${1:-}" == "--fresh" ]]; then
    echo "Clearing processed-message tracker..."
    rm -f "$WORKDIR/inbox/.processed"
fi

# Kill existing session if present
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Killing existing session '$SESSION'..."
    tmux kill-session -t "$SESSION"
fi

# Create new session
tmux new-session -d -s "$SESSION" -c "$WORKDIR" -x 220 -y 50
tmux rename-window -t "$SESSION:0" "cleo"

# Start Claude Code
tmux send-keys -t "$SESSION" "(claude --dangerously-skip-permissions --continue 2>/dev/null || claude --dangerously-skip-permissions)" Enter

echo ""
echo "Cleo started in tmux session '$SESSION'"
echo "  Attach: tmux attach -t $SESSION"
echo "  Detach: Ctrl-b d"
