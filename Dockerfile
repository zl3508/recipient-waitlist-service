FROM python:3.11-slim

# 工作目录
WORKDIR /app

# 先复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制全部代码
COPY . .

# 启动 FastAPI（Cloud Run 会注入 PORT 环境变量）
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
