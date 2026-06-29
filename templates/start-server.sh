#!/usr/bin/env bash
# start-server.sh — 报告 HTTP 服务器一键启动
# 用法: bash start-server.sh
# 使用 Python 内置 HTTP 服务器静默后台运行
# 停止: kill $(cat .server.pid) && rm .server.pid

PORT=${1:-8000}
PID_FILE=".server.pid"
DEFAULT=""

if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
  echo "服务器已在运行 (PID $(cat $PID_FILE))，端口 $PORT"
  echo "停止: kill $(cat $PID_FILE) && rm $PID_FILE"
  exit 0
fi

if [ -f "index.html" ]; then
  DEFAULT="http://localhost:$PORT/index.html"
else
  FIRST=$(ls *.html 2>/dev/null | sort | head -1)
  if [ -n "$FIRST" ]; then
    DEFAULT="http://localhost:$PORT/$FIRST"
  else
    DEFAULT="http://localhost:$PORT/"
  fi
fi

nohup python3 -m http.server "$PORT" --bind 127.0.0.1 > /dev/null 2>&1 &
echo $! > "$PID_FILE"

echo "=== context2html 报告服务器 ==="
echo "端口: $PORT"
echo "PID: $(cat $PID_FILE)"
echo "打开: $DEFAULT"
echo "停止: kill $(cat $PID_FILE) && rm $PID_FILE"
echo ""

if command -v open &>/dev/null; then
  open "$DEFAULT"
elif command -v xdg-open &>/dev/null; then
  xdg-open "$DEFAULT"
fi
