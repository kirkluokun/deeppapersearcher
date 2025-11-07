#!/bin/bash

# arXiv 论文检索系统启动脚本
# 同时启动后端和前端服务

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  arXiv 论文检索系统启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查后端目录
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}错误: 后端目录不存在: $BACKEND_DIR${NC}"
    exit 1
fi

# 检查前端目录
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}错误: 前端目录不存在: $FRONTEND_DIR${NC}"
    exit 1
fi

# 检查 .env 文件（先检查根目录，再检查 backend 目录）
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${GREEN}找到 .env 文件: $SCRIPT_DIR/.env${NC}"
elif [ -f "$BACKEND_DIR/.env" ]; then
    echo -e "${GREEN}找到 .env 文件: $BACKEND_DIR/.env${NC}"
else
    echo -e "${RED}警告: 未找到 .env 文件，请确保已配置 GEMINI_API_KEY${NC}"
    echo -e "${BLUE}提示: 可以在 $SCRIPT_DIR/.env 或 $BACKEND_DIR/.env 中设置 GEMINI_API_KEY${NC}"
fi

# 函数：清理后台进程
cleanup() {
    echo ""
    echo -e "${BLUE}正在停止服务...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 启动后端
echo -e "${BLUE}启动后端服务...${NC}"
cd "$BACKEND_DIR"
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}后端启动失败，请查看 backend.log${NC}"
    exit 1
fi

echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}后端日志: $SCRIPT_DIR/backend.log${NC}"
echo ""

# 启动前端
echo -e "${BLUE}启动前端服务...${NC}"
cd "$FRONTEND_DIR"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}检测到未安装依赖，正在安装...${NC}"
    npm install
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
sleep 3

# 检查前端是否启动成功
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}前端启动失败，请查看 frontend.log${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo -e "${BLUE}前端日志: $SCRIPT_DIR/frontend.log${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  服务启动成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}后端 API:${NC} http://localhost:8001"
echo -e "${BLUE}前端应用:${NC} http://localhost:3000"
echo ""
echo -e "${BLUE}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 等待用户中断
wait

