# Node.js 20 경량화 이미지
FROM node:20-alpine

# 컨테이너 내 작업 디렉터리 지정
WORKDIR /app

# 패키지 명세서 복사 및 설치 (캐싱 활용)
COPY package*.json ./
RUN npm install

# 소스 코드 전체 복사
COPY . .

# Vite 개발 서버 포트 명시
EXPOSE 5173

# Vite 개발 서버 실행 (외부 바인딩을 위해 --host 필수)
CMD ["npm", "run", "dev", "--", "--host"]