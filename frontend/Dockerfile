FROM node:20

# 设置工作目录
WORKDIR /app

COPY www/package*.json .
# 安装依赖
RUN npm install

# 将本地 bin 加入 PATH
ENV PATH=/app/node_modules/.bin:$PATH

# 复制www目录下的源码
COPY www/ .

# 暴露端口
EXPOSE 5173

# 启动开发服务器
CMD ["vite"]