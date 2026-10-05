<p align="center">
  <img width="320" height="160" alt="제목을 입력해주세요" src="https://github.com/user-attachments/assets/16b11e24-2fb2-4af4-9e82-ca2df49853d2" />
</p>
<p align="center">
  <strong>재건축 재개발 분담금 예측을 간편하게 사용해보세요.</strong>
</p>

<p align="center">
  얼마 GEO 는 지도를 통하여 간편하게 구간에 대하여
  AI 를 사용한 분담금 예측을 진행해주는 웹 서비스입니다.
</p>

<img width="1024" height="570" alt="제목을 입력해주세요  (4)" src="https://github.com/user-attachments/assets/438b2688-6835-4e64-8358-20f1aca91e63" />

# 1. 서비스 개요
- 서비스 링크
  - https://04-howmuch-geo-ntnl.vercel.app/
- 서비스 설명
  - 얼마 GEO 는 지도를 통하여 간편하게 구간에 대하여 AI 를 사용한 분담금 예측을 진행해주는 웹 서비스입니다.

# 2. 기술 스택

| 구분                 | 기술 스택                                               |
|:---------------------|:--------------------------------------------------------|
| Frontend             | Tailwind, Typescript, Prettier, Axios, Vite             |
| Backend              | Python, FastAPI, httpx, PostgreSQL, Redis               |
| API                  | Kakao SDK API, V-World API, 공공데이터포털 API           |
| CI/CD                | Vercel, Render, Github Action                           |

# 3. 주요 기능
- 백엔드 엔드포인트

| 엔드포인트                     | 설명                                                    |
|:-------------------------------|:--------------------------------------------------------|
| GET /api/v1/cadastral          | 필지 조회 API                                            |
| POST /api/v1/zone              | 슬라이더 및 기본 정보 조합 API                            |
| POST /api/v1/contribution      | 최종 분담금 계산 API                                     |
| POST /api/v1/user/signup       | 사용자 회원가입 API                                      |
| POST /api/v1/user/login        | 사용자 로그인 API                                        |
|  GET /api/v1/user/logout       | 사용자 로그아웃 API                                      |
| GET /api/v1/user/info          | 사용자 정보 조회 API                                     |
| POST /api/v1/news              | 지역 이름을 바탕으로 뉴스 조회 API                        |

# 4. 아키텍쳐

- 시스템 아키텍쳐
<img width="1671" height="1402" alt="System Arcitecture drawio" src="https://github.com/user-attachments/assets/abbc89b0-16cf-4ba6-9382-bc892c4b1494" />

- ERD
<img width="142" height="134" alt="제목 없는 다이어그램 drawio" src="https://github.com/user-attachments/assets/f3ec0c0d-6d89-49f4-ad05-688da4c4b61b" />

- Directory 아키텍쳐
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
├── backend
│   ├── Dockerfile
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


