#!/bin/zsh
# pyq001 — Claude Remote Control 시작 스크립트
# EGP v4.0 | Bootstrap Mode
#
# 사용법: ./scripts/start_remote.sh
# 재접속:  screen -r pyq001

CLAUDE_BIN="/Users/qy3rvnmrm/.vscode/extensions/anthropic.claude-code-2.1.74-darwin-arm64/resources/native-binary/claude"
PROJECT_DIR="/Users/qy3rvnmrm/pyq001"
SESSION_NAME="pyq001"

# PATH에 claude 추가
export PATH="$HOME/.local/bin:$PATH"

# 이미 실행 중인 screen 세션 확인
if screen -list 2>/dev/null | grep -q "$SESSION_NAME"; then
    echo "▶ 이미 실행 중인 세션 발견: $SESSION_NAME"
    echo "  재접속: screen -r $SESSION_NAME"
    screen -r "$SESSION_NAME"
    exit 0
fi

echo "▶ pyq001 remote-control 세션 시작..."
echo "  프로젝트: $PROJECT_DIR"
echo "  Claude: $CLAUDE_BIN"
echo ""

# screen 세션 생성 및 claude remote-control 실행
screen -dmS "$SESSION_NAME" bash -c "
    cd '$PROJECT_DIR'
    export PATH='$HOME/.local/bin:\$PATH'
    echo 'pyq001 세션 시작됨 — $(date)'
    '$CLAUDE_BIN' remote-control --name 'pyq001 Elliott Wave'
    echo 'remote-control 종료됨'
    exec bash
"

sleep 1

if screen -list 2>/dev/null | grep -q "$SESSION_NAME"; then
    echo "✓ 세션 시작 완료"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  접속:    screen -r $SESSION_NAME"
    echo "  분리:    Ctrl+A, D"
    echo "  종료:    screen -S $SESSION_NAME -X quit"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "▶ 세션에 접속합니다..."
    sleep 0.5
    screen -r "$SESSION_NAME"
else
    echo "✗ 세션 시작 실패"
    exit 1
fi
