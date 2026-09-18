# 파이썬 3.11 경량화 이미지
FROM python:3.11-slim

# 컨테이너 내 작업 디렉터리 지정
WORKDIR /app

# 기본 C 빌드 도구 설치 (C-extension 모듈용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 라이브러리 목록 복사 및 설치 (캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# FastAPI 서버 포트 명시
EXPOSE 8000

# uvicorn 실행 (코드 수정 시 자동 재시작 --reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]