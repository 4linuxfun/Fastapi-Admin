#!/bin/bash
# 生产、开发环境服务控制
# service.sh dev|pro start|stop|restart

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

start_fastapi() {
    env=$1
    if pgrep -f "gunicorn server.main:app" > /dev/null || pgrep -f "uvicorn server.main:app" > /dev/null; then
        echo "FastAPI service is already running."
        return 1
    fi
    
    echo "Starting FastAPI service..."
    cd "$SCRIPT_DIR"
    
    if [ "$env" = "pro" ]; then
        echo "Running in production mode..."
        export ENV=production
        nohup gunicorn server.main:app \
            -b 127.0.0.1:8000 \
            -w 4 \
            -k uvicorn.workers.UvicornWorker \
            > gunicorn.log 2>&1 &
    else
        echo "Running in development mode..."
        export ENV=development
        nohup python -m uvicorn server.main:app \
            --host 0.0.0.0 --port 8000 \
            --reload \
            --reload-exclude www \
            > fastapi_dev.log 2>&1 &
    fi
}

stop_fastapi() {
    if ! pgrep -f "gunicorn server.main:app" > /dev/null && ! pgrep -f "uvicorn server.main:app" > /dev/null; then
        echo "FastAPI service is not running."
        return 1
    fi
    echo "Stopping FastAPI service..."
    pkill -f "gunicorn.*server.main:app"
    pkill -9 -f "python.*-m.*uvicorn.*server.main:app"
    # 关闭所有相关的 Python 子进程
    pkill -9 -f "multiprocessing-fork"
    # 确保端口被释放
    fuser -k 8000/tcp
}

start_scheduler() {
    echo "Starting RPyC scheduler..."
    cd "$SCRIPT_DIR"
    if [ "$1" = "pro" ]; then
        export ENV=production
    else
        export ENV=development
    fi
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    nohup python rpyc_scheduler/server.py > rpyc_scheduler.log 2>&1 &
}

stop_scheduler() {
    echo "Stopping RPyC scheduler..."
    pkill -f "python.*server.py"
}

case "$2" in
    start)
        start_fastapi "$1"
        start_scheduler "$1"
        ;;
    stop)
        stop_fastapi
        stop_scheduler
        ;;
    restart)
        stop_fastapi
        stop_scheduler
        sleep 2
        start_fastapi "$1"
        start_scheduler "$1"
        ;;
    *)
        echo "Usage: $0 {dev|pro} {start|stop|restart}"
        echo "Options:"
        echo "  dev     Development environment"
        echo "  pro     Production environment"
        echo "Commands:"
        echo "  start   Start services"
        echo "  stop    Stop services"
        echo "  restart Restart services"
        exit 1
        ;;
esac
