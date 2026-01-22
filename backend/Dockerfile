FROM python:3.12

WORKDIR /app
# RUN apt-get update && apt-get install -y build-essential libffi-dev libyaml-dev

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 直接将应用代码拷贝到/app目录，避免嵌套结构
COPY ./app /app

CMD ["fastapi","dev","main.py","--host","0.0.0.0","--port","8000"]
