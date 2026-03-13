#!/bin/zsh
# pyq001 — Remote Control 세션 종료

SESSION_NAME="pyq001"

if screen -list 2>/dev/null | grep -q "$SESSION_NAME"; then
    screen -S "$SESSION_NAME" -X quit
    echo "✓ 세션 종료: $SESSION_NAME"
else
    echo "실행 중인 세션 없음"
fi
