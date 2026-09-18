import { useState, useEffect } from 'react'

// 현실적인 범위 내 무작위 입력값 생성 함수
const getRandomValues = () => ({
  area: Number((Math.random() * (150 - 20) + 20).toFixed(1)), // 20.0 ~ 150.0 m²
  floor: Math.floor(Math.random() * 30) + 1,                 // 1 ~ 30층
  building_ages: Math.floor(Math.random() * 30),             // 0 ~ 29년
  subway_distance: Math.floor(Math.random() * 1450) + 50,    // 50 ~ 1500m
})

function App() {
  const [formData, setFormData] = useState({
    area: 84.5,
    floor: 10,
    building_ages: 5,
    subway_distance: 300,
  })

  // 자동 무작위 변경 토글 상태
  const [isAutoRandom, setIsAutoRandom] = useState(false)

  const [predictedPrice, setPredictedPrice] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  // 자동 무작위 실행 (2초 간격)
  useEffect(() => {
    let intervalId
    if (isAutoRandom) {
      intervalId = setInterval(() => {
        setFormData(getRandomValues())
      }, 2000)
    }
    return () => clearInterval(intervalId)
  }, [isAutoRandom])

  // 수동 무작위 설정 버튼 클릭 핸들러
  const handleRandomize = () => {
    setFormData(getRandomValues())
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value === '' ? '' : Number(value),
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // 백엔드 요청 스키마(building_age 단수/복수 여부 체크 후 맞춤)
    const payload = {
      area: Number(formData.area),
      floor: Number(formData.floor),
      building_age: Number(formData.building_ages),
      subway_distance: Number(formData.subway_distance),
    }

    try {
      const response = await fetch(`${backendUrl}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(JSON.stringify(errorData.detail) || '예측 실패')
      }

      const data = await response.json()
      setPredictedPrice(data.predicted_price)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-6 font-sans">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
        <h1 className="text-2xl font-bold text-slate-800 mb-1">부동산 가격 예측</h1>
        <p className="text-sm text-slate-500 mb-6">입력값을 무작위로 생성하여 테스트해보세요.</p>

        {/* 무작위 생성 컨트롤 버튼 영역 */}
        <div className="flex gap-2 mb-6">
          <button
            type="button"
            onClick={handleRandomize}
            className="flex-1 py-2 px-3 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition"
          >
            🎲 무작위 값 넣기
          </button>
          <button
            type="button"
            onClick={() => setIsAutoRandom(!isAutoRandom)}
            className={`flex-1 py-2 px-3 text-xs font-semibold rounded-lg transition ${
              isAutoRandom
                ? 'bg-amber-500 hover:bg-amber-600 text-white animate-pulse'
                : 'bg-slate-200 hover:bg-slate-300 text-slate-700'
            }`}
          >
            {isAutoRandom ? '⏹️ 자동 변경 중지' : '🔄 2초마다 자동 변경'}
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">면적 (area)</label>
            <input
              type="number"
              name="area"
              step="any"
              value={formData.area}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">층수 (floor)</label>
            <input
              type="number"
              name="floor"
              value={formData.floor}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">건물 연식 (building_ages)</label>
            <input
              type="number"
              name="building_ages"
              value={formData.building_ages}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1">역 거리 (subway_distance)</label>
            <input
              type="number"
              name="subway_distance"
              value={formData.subway_distance}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition duration-200 disabled:opacity-50"
          >
            {loading ? '예측 요청 중...' : '가격 예측하기'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs break-all">
            {error}
          </div>
        )}

        {predictedPrice !== null && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg text-center">
            <span className="text-sm font-medium text-green-700 block mb-1">예측 가격</span>
            <span className="text-2xl font-extrabold text-green-900">
              {predictedPrice.toLocaleString('ko-KR', { maximumFractionDigits: 2 })} 만원
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default App