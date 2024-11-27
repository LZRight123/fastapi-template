# 使用 Python 3.13 poetry 作为基础镜像
FROM deerliang/python3.13-poetry:latest 

WORKDIR /app

# # 复制 pyproject.toml 和 poetry.lock 文件到 /tmp 目录
# # poetry.lock 后的星号表示这个文件可能不存在，如果不存在也不会报错
COPY ./pyproject.toml ./poetry.lock* /app/

# # 使用 Poetry 导出依赖到 requirements.txt 文件
# # --without-hashes 选项避免在 requirements.txt 中包含包的哈希值
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN rm -rf /app/pyproject.toml /app/poetry.lock*


# # 使用 pip 安装 requirements.txt 中列出的所有依赖
# # --no-cache-dir 选项防止 pip 缓存下载的包，减小镜像大小
# # --upgrade 选项确保安装最新版本的包
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
# # 设置环境变量 PYTHONPATH，确保 Python 可以找到应用程序模块
ENV PYTHONPATH=/app
# # 设置环境变量 WORKERS_PER_CORE，可能用于配置 ASGI 服务器的工作进程数
# ENV WORKERS_PER_CORE=2

# # 复制本地的 ./app 目录到容器的 /app/app 目录
COPY ./app /app/app
# # 复制数据库迁移配置文件到容器的 /app/ 目录
COPY ./alembic.ini /app/
# # 复制启动脚本到容器的 /app/ 目录
COPY ./start.sh /app/
COPY ./.env /app/app
# # 给启动脚本添加执行权限
RUN chmod +x /app/start.sh

