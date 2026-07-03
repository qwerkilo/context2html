#!/usr/bin/env bash
# start-server.sh — 报告 HTTP 服务器一键启动
# 用法: bash start-server.sh [PORT]   (默认 8000)
# 使用 Python 内置 HTTP 服务器静默后台运行
# 停止: kill $(cat .server.pid) && rm .server.pid

set -e
PORT=${1:-8000}
PID_FILE=".server.pid"
DEFAULT=""

# 检查旧服务器进程是否仍在运行（容错处理：PID 文件不存在或进程已死亡）
is_running() {
  local pid
  [ -f "$PID_FILE" ] || return 1
  pid=$(tr -d '[:space:]' < "$PID_FILE")
  [ -n "$pid" ] || return 1
  kill -0 "$pid" 2>/dev/null
}

if is_running; then
  echo "服务器已在运行 (PID $(tr -d '[:space:]' < "$PID_FILE"))，端口 $PORT"
  echo "停止: kill \$(cat $PID_FILE) && rm $PID_FILE"
  exit 0
else
  # 清理陈旧的 PID 文件
  [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
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

# 启动服务器并立即记 PID（写到磁盘后再返回）
nohup python3 -m http.server "$PORT" --bind 127.0.0.1 > /dev/null 2>&1 &
SERVER_PID=$!
printf '%s' "$SERVER_PID" > "$PID_FILE"

# 等待端口可用（避免覆盖旧 PID 文件的竞态）
for i in 1 2 3 4 5; do
  if kill -0 "$SERVER_PID" 2>/dev/null && \
     (echo > /dev/tcp/127.0.0.1/"$PORT") 2>/dev/null; then
    break
  fi
  sleep 0.2
done

echo "=== context2html 报告服务器 ==="
echo "端口: $PORT"
echo "PID: $SERVER_PID"
echo "打开: $DEFAULT"
echo "停止: kill \$(cat $PID_FILE) && rm $PID_FILE"
echo ""

if command -v open &>/dev/null; then
  open "$DEFAULT"
elif command -v xdg-open &>/dev/null; then
  xdg-open "$DEFAULT"
fi
