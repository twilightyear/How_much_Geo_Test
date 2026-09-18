npm create vite@latest frontend -- --template react
npm install
npm install axios
npm install -D tailwindcss @tailwindcss/vite

@import "tailwindcss"; on /src/index.css

vite.config.js 에 아래 코드 삽입
import tailwindcss from '@tailwindcss/vite'
tailwindcss(),
