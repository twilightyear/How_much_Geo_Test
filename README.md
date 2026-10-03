<p align="center">
  <img width="120" height="120" alt="제목을 입력해주세요 - 복사본 (1)" src="https://github.com/user-attachments/assets/7e12d708-032d-4e46-a5e8-25bd43b77d45" />
</p>
<h1 align="center">
  얼마 GEO
</h1>
<p align="center">
  <strong>재건축 재개발 분담금 예측을 간편하게 사용해보세요.</strong>
</p>

<p align="center">
  얼마 GEO 는 지도를 통하여 간편하게 구간에 대하여
  AI 를 사용한 분담금 예측을 진행해주는 웹 서비스입니다.
</p>

<img width="1024" height="570" alt="제목을 입력해주세요  (4)" src="https://github.com/user-attachments/assets/438b2688-6835-4e64-8358-20f1aca91e63" />

# 1. 서비스 링크

https://04-howmuch-geo-ntnl.vercel.app/

# 2. 기술 스택
- Frontend : Tailwind, Typescript, (Prettier), Axios, Vite, Vercel
- Backend : Python, FastAPI, httpx, PostgreSQL, Redis, Render, Vercel, V-World API, Kakao SDK API

# 3. 주요 기능
## 3.1. 백엔드 엔드포인트
- /api/vi/cadastral
- /api/vi/zone
- /api/vi/contribution
- /api/vi/user/signup
- /api/vi/user/login
- /api/vi/user/logout
- /api/vi/user/info

# 4. 아키텍쳐

# 4.1 Directory 아키텍쳐
```
├── AI
│   ├── engine
│   │   ├── calc.py
│   │   ├── rental_cost.py
│   │   ├── schema.py
│   │   └── zone.py
│   └── predict
│       ├── construction_cost.py
│       ├── data
│       ├── predictions.py
│       ├── sale_price.py
│       └── trend.py
├── README.md
├── backend
│   ├── Dockerfile
│   ├── README.md
│   ├── app
│   │   ├── auth
│   │   ├── config
│   │   ├── core
│   │   ├── database
│   │   ├── exceptions
│   │   ├── main.py
│   │   ├── models
│   │   ├── routers
│   │   ├── schemas
│   │   └── utils
│   └── requirements.txt
├── docker-compose.yml
├── frontend
│   ├── Dockerfile
│   ├── README.md
│   ├── WARNING_COPY.md
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── public
│   │   ├── favicon.png
│   │   └── icons.svg
│   ├── src
│   │   ├── App.tsx
│   │   ├── api
│   │   ├── components
│   │   ├── hooks
│   │   ├── index.css
│   │   ├── main.tsx
│   │   ├── pages
│   │   └── utils
│   ├── tsconfig.json
│   └── vite.config.ts
└── vercel.json
```
