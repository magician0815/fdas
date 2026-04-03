# FDAS Makefile
# 常用命令快捷方式

.PHONY: help install dev test build docker-up docker-down clean

help:
	@echo "FDAS - 金融数据抓取与分析系统"
	@echo ""
	@echo "使用方式: make [命令]"
	@echo ""
	@echo "命令列表:"
	@echo "  install      安装所有依赖"
	@echo "  dev          启动开发环境"
	@echo "  test         运行所有测试"
	@echo "  build        构建生产版本"
	@echo "  docker-up    启动Docker环境"
	@echo "  docker-down  停止Docker环境"
	@echo "  clean        清理临时文件"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	cd backend && uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev

test:
	cd backend && pytest
	cd frontend && npm run test

build:
	cd frontend && npm run build

docker-up:
	cd docker && docker-compose up -d

docker-down:
	cd docker && docker-compose down

clean:
	rm -rf backend/__pycache__ backend/app/__pycache__
	rm -rf backend/logs/*.log
	rm -rf frontend/dist
	rm -rf .coverage htmlcov