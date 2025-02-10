#!/bin/bash
# 生产、开发环境服务控制
# service.sh dev|pro start|stop|restart

start_fastapi() {
  env=$1
  if pgrep -f "gunicorn server.main:app" > /dev/null || pgrep -f "uvicorn server.main:app" > /dev/null; then
    echo "FastAPI service is already running."
    return 1
  fi
  echo "Starting FastAPI service..."
  if [ "$env" = "pro" ]; then
    echo "Running in production mode..."
    nohup gunicorn server.main:app -b 127.0.0.1:8000 -w 4 -k uvicorn.workers.UvicornWorker >gunicorn.log 2>&1&
  else
    echo "Running in development mode..."
    nohup uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude www > fastapi_dev.log 2>&1&
  fi

}

stop_fastapi() {
  env=$1
  if ! pgrep -f "gunicorn server.main:app" > /dev/null && ! pgrep -f "uvicorn server.main:app" > /dev/null; then
    echo "FastAPI service is not running."
    return 1
  fi
  echo "Stopping FastAPI service..."
  if [ "$env" = "pro" ]; then
    echo "Running in production mode..."
    pkill -f "gunicorn server.main:app"
  else
    echo "Running in development mode..."
    pkill -f "uvicorn server.main:app"
  fi
}

restart_fastapi() {
  stop_fastapi "$1"
  start_fastapi "$1"
}

start_rpyc() {
  echo "Starting RPyc service..."
  cd ./rpyc_scheduler && nohup python3.9 scheduler-server.py > ../rpyc_scheduler.log 2>&1&
  cd ..
}

stop_rpyc() {
  echo "Stopping RPyc service..."
  pkill -f "python scheduler-server.py"
}

restart_rpyc() {
  stop_rpyc
  start_rpyc
}

case "$2" in
  start)
    start_fastapi "$1"
    start_rpyc
    ;;
  stop)
    stop_fastapi "$1"
    stop_rpyc
    ;;
  restart)
    restart_fastapi "$1"
    restart_rpyc
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
