#!/bin/bash
# start_all.sh
# 运行 React 静态服务 + MinIO + Nest 开发服务器 + Cloudflare Tunnel

# 启动 React 静态服务
echo "Starting React static server on port 5173..."
(
  cd /xf/react-ali-ai/dist || exit
  python3 -m http.server 5173 &
)

# 启动 MinIO 服务
echo "Starting MinIO server on port 9000 (console on 9001)..."
(
  cd /xf/minio || exit
  ./minio server /xf/minio-memory --console-address ":9001" &
)

# 启动 Nest 开发服务器
echo "Starting NestJS dev server..."
(
  cd /xf/nest-ali-ai || exit
  npm run start:dev &
)

# 等待 4 秒让服务初始化
sleep 4

# 启动 Cloudflare Tunnel
echo "Starting Cloudflare tunnel..."
cloudflared tunnel run termux-tunnel
