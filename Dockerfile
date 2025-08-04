# 베이스 이미지: Python 3.10
FROM python:3.10-slim

# 시스템 패키지 업데이트 및 JDK 설치
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \
    curl \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && apt-get clean

# JAVA_HOME 환경변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 먼저 복사하고 의존성 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 전체 프로젝트 복사
COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# uvicorn 서버 실행 (포트 8000)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
