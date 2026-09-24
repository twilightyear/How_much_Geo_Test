# 분담금 엔진 백엔드 연동 가이드

AI 엔진(`AI/engine/`)을 FastAPI 백엔드에 붙이는 방법입니다.
엔진은 HTTP를 전혀 모르고 **순수 데이터(dataclass)만 주고받습니다.** 백엔드가 할 일은 세 가지입니다.

1. V-World 응답 → `ParcelInfo` 변환
2. 엔진 호출 (`build_zone_summary` → `calc_*`)
3. 결과 dataclass → JSON 직렬화

변수 하나하나의 의미와 값은 `var.md`를 참고하세요. 이 문서는 **연동 방법**만 다룹니다.

---

## 0. 먼저 해결해야 할 것: 엔진 파일 경로

지금 엔진은 저장소 루트의 `AI/engine/`에 있고, 백엔드 Docker 이미지는 `backend/` 를 빌드 컨텍스트로 씁니다. **그대로는 컨테이너 안에서 엔진을 import할 수 없습니다.** 셋 중 하나를 골라 주세요.

| 방법 | 내용 | 비고 |
|---|---|---|
| A. 엔진을 backend 안으로 | `AI/engine/` → `backend/app/engine/` 으로 이동 | 가장 단순. import도 `from app.engine.calc import ...` |
| B. 빌드 컨텍스트 변경 | `docker-compose.yml` 의 backend `context` 를 저장소 루트로 바꾸고 `AI/` 를 복사 | 엔진 위치를 유지 |
| C. sys.path 추가 | 앱 시작 시 `sys.path.append("/app/AI/engine")` | 임시방편. 경로가 꼬이기 쉬움 |

**A를 추천합니다.** 엔진은 AI 파트가 계속 고치지만 배포는 백엔드와 함께 나가므로, 한 이미지 안에 있는 편이 낫습니다.

**Python 3.10 이상이어야 합니다.** 엔진이 `float | None` 문법을 씁니다. 현재 이미지 버전을 확인해 주세요.

---

## 1. API 두 개

### 1-1. `POST /zone` — 필지 선택 → 구역 정보

프론트가 지도에서 고른 PNU 목록을 보내면, 구역 면적·용적률 범위·슬라이더 초기값을 돌려줍니다.

**요청**
```json
{ "pnus": ["1111010100100010000", "1111010100100020000"] }
```

**응답**
```json
{
  "zone": {
    "site_area_m2": 12450.5,
    "far_min": 210.6,
    "far_max": 260.6,
    "land_value_total": 366500,
    "pnus": ["...", "..."],
    "warnings": ["용도지역이 섞여 있어 면적 가중평균을 사용했습니다: ..."]
  },
  "sliders": {
    "floor_area_ratio":  { "value": 210.6, "min": 210.6, "max": 260.6 },
    "member_price_ratio":{ "value": 0.8,   "min": 0.7,   "max": 0.9 },
    "other_cost_ratio":  { "value": 0.35,  "min": 0.25,  "max": 0.45 },
    "commercial_ratio":  { "value": 0.03,  "min": 0.0,   "max": 0.2 },
    "construction_cost_per_pyeong": { "value": 850, "min": 700, "max": 1000 },
    "general_price_per_m2":         { "value": 998.25, "min": 700, "max": 1300 },
    "proportional_rate": { "value": 100, "min": 80, "max": 120, "fixed": true }
  }
}
```

슬라이더의 `min`/`max`는 백엔드 설정값이고, `floor_area_ratio` 만 `ZoneSummary` 에서 나옵니다.

### 1-2. `POST /contribution` — 슬라이더 값 + 개인 정보 → 분담금

**요청**
```json
{
  "site_area_m2": 12450.5,
  "member_count": 700,
  "sliders": {
    "floor_area_ratio": 250,
    "member_price_ratio": 0.8,
    "other_cost_ratio": 0.35,
    "commercial_ratio": 0.03,
    "construction_cost_per_pyeong": 850,
    "general_price_per_m2": 998.25,
    "proportional_rate": 100
  },
  "owner": { "desired_unit": "84", "official_price": 35000 }
}
```

**응답**
```json
{
  "contribution": 44263,
  "right_value": 45500,
  "member_price": 89763,
  "prior_asset": 45500,
  "proportional_rate": 100.0,
  "rate_fixed": true,
  "project": {
    "total_cost": 69423438,
    "total_post_asset": 92860000,
    "total_prior_asset": 24500000,
    "gross_floor_area_m2": 200000,
    "commercial_area_m2": 3750
  },
  "unit_options": [
    { "name": "59",  "supply_area_m2": 82.64,  "count": 355, "member_price": 65996 },
    { "name": "84",  "supply_area_m2": 112.40, "count": 472, "member_price": 89763 },
    { "name": "114", "supply_area_m2": 148.76, "count": 82,  "member_price": 118800 }
  ],
  "warnings": ["비례율 고정값(100.0%) 사용 : 사업비·분양가 변화가 반영되지 않습니다."]
}
```

- **금액은 모두 만원, 면적은 ㎡입니다.** 프론트에서 "억" 표시는 `/10000` 하세요.
- `unit_options` 는 평형 선택 버튼 목록입니다. 사용자가 버튼을 누르면 `owner.desired_unit` 에 `name` 을 그대로 담아 다시 요청하면 됩니다.
- `warnings` 는 화면에 안내 문구로 그대로 띄우면 됩니다.

---

## 2. V-World 응답 → `ParcelInfo` 변환

`build_zone_summary()` 는 `ParcelInfo` 리스트를 받습니다.

| ParcelInfo 필드 | V-World 필지 응답 | 비고 |
|---|---|---|
| `pnu` | `properties.pnu` | 그대로 |
| `land_price_per_m2` | `properties.jiga` | **원/㎡ 단위 그대로** 넣는다 (엔진이 만원으로 환산) |
| `area_m2` | **없음** | 아래 참고 |
| `zoning` | **없음** | 아래 참고 |
| `land_category` | **없음** | 없으면 `None` |

### 없는 값 두 개를 채우는 방법

**면적 `area_m2`**
- (권장) 토지특성정보 API를 PNU로 조회해 공부상 면적을 가져옵니다. 용도지역·지목도 같이 나옵니다.
- (대안) 필지 폴리곤으로 계산합니다. 좌표가 위경도(EPSG:4326)라 **그대로 면적을 구하면 틀립니다.** 평면좌표(EPSG:5186 등)로 변환 후 계산하세요.
  ```python
  from pyproj import Transformer
  from shapely.geometry import shape
  from shapely.ops import transform

  to_5186 = Transformer.from_crs("EPSG:4326", "EPSG:5186", always_xy=True).transform
  area_m2 = transform(to_5186, shape(feature["geometry"])).area
  ```
  `requirements.txt` 에 `pyproj`, `shapely` 추가가 필요합니다.

**용도지역 `zoning`**
- 토지특성정보 API에서 받습니다. **용적률 슬라이더 범위를 정하는 값이라 없으면 안 됩니다.**
- 문자열이 `"제2종일반주거지역"` 형태여야 엔진의 `FAR_TABLE` 과 맞습니다. 공백은 엔진이 제거하지만, `"2종일반주거"` 처럼 표기가 다르면 매칭되지 않고 경고만 남습니다.
- **실제 응답 문자열을 한 번 찍어서 AI 파트에 알려 주세요.** 표를 맞추겠습니다.

### 변환 코드 예시
```python
from app.engine.schema import ParcelInfo   # 경로는 0절에서 정한 방식에 맞춰

def to_parcel_info(feature: dict, area_m2: float, zoning: str, land_category: str | None = None):
    props = feature["properties"]
    return ParcelInfo(
        pnu=props["pnu"],
        area_m2=area_m2,
        land_price_per_m2=float(props["jiga"]),
        zoning=zoning,
        land_category=land_category,
    )
```

---

## 3. 가정치 기본값

엔진은 **기본값을 갖고 있지 않습니다.** 값을 빠뜨리면 조용히 넘어가지 않고 에러가 나도록 일부러 그렇게 만들었습니다. 슬라이더로 받지 않는 값들은 백엔드 설정에 두세요.

```python
# app/config/engine_defaults.py
ENGINE_DEFAULTS = {
    "underground_ratio": 0.6,            # 지하 연면적 / 지상 연면적
    "community_ratio": 0.05,             # 커뮤니티·부대복리 비율
    "housing_supply_efficiency": 0.97,   # 주택 연면적 → 공급면적 전환율
    "commercial_price_ratio": 1.2,       # 상가 분양가 = 일반분양가 × 배수
    "rental_ratio": 0.15,                # 임대 비율 (면적 기준)
    "rental_supply_area_m2": 59.0,       # 임대 1세대 공급면적
    "rental_price_per_unit": 30_000,     # 임대 1세대 인수가(만원)
    "avg_prior_asset": 35_000,           # 조합원 평균 종전자산(만원) — 임시 가정치
    "appraisal_ratio": 1.3,              # 감정평가액 / 공시가격 보정률
}

UNIT_MIX = [   # 평형 구성. share 합계는 반드시 1.0
    {"name": "59",  "exclusive_area_m2": 59.0,  "supply_area_m2": 82.64,  "share": 0.31},
    {"name": "84",  "exclusive_area_m2": 84.0,  "supply_area_m2": 112.40, "share": 0.56},
    {"name": "114", "exclusive_area_m2": 114.0, "supply_area_m2": 148.76, "share": 0.13},
]
```

이 값들은 **월계1동 기준 가정치**이며, 정비계획 자료를 구하면 교체합니다. 한곳에 모아 두면 나중에 바꾸기 쉽습니다.

---

## 4. 라우터 예시

```python
from dataclasses import asdict
from fastapi import APIRouter, HTTPException

from app.config.engine_defaults import ENGINE_DEFAULTS, UNIT_MIX
from app.engine.calc import calc_allocation, calc_area, calc_contribution, unit_options
from app.engine.schema import OwnerInput, ProjectParams, ProjectType, UnitMix
from app.engine.zone import build_zone_summary

router = APIRouter(tags=["Contribution"])


@router.post("/zone")
async def get_zone(req: ZoneRequest):
    parcels = [...]                     # 2절 변환
    try:
        zone = build_zone_summary(parcels)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"zone": asdict(zone), "sliders": build_sliders(zone)}


@router.post("/contribution")
async def get_contribution(req: ContributionRequest):
    params = ProjectParams(
        name=req.name or "사용자 지정 구역",
        project_type=ProjectType.REDEVELOPMENT,
        site_area_m2=req.site_area_m2,
        member_count=req.member_count,
        unit_mix_list=[UnitMix(**m) for m in UNIT_MIX],
        **req.sliders.model_dump(),      # 슬라이더 값
        **ENGINE_DEFAULTS_FOR_PARAMS,    # appraisal_ratio 는 OwnerInput 쪽이므로 제외
    )
    owner = OwnerInput(
        desired_unit=req.owner.desired_unit,
        official_price=req.owner.official_price,
        appraisal_ratio=ENGINE_DEFAULTS["appraisal_ratio"],
    )

    try:
        areas = calc_area(params)
        alloc = calc_allocation(params, areas)
        result = calc_contribution(params, alloc, owner)
        options = unit_options(params, alloc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        **asdict(result),
        "unit_options": [asdict(o) for o in options],
        "warnings": result.project.warnings,
    }
```

**핵심 세 가지**
- `ProjectParams` 는 **키워드 인자로만** 생성됩니다. 위치 인자로는 만들 수 없습니다.
- 엔진의 `ValueError` 는 전부 **입력이 잘못된 경우**이므로 `400` 으로 내보내면 됩니다. 메시지는 한글로 그대로 쓸 수 있습니다.
- 결과 dataclass는 `dataclasses.asdict()` 로 dict가 됩니다. 응답 스키마를 pydantic으로 따로 정의해도 됩니다.

---

## 5. 에러와 경고 구분

| 종류 | 언제 | 처리 |
|---|---|---|
| `ValueError` | 계산이 불가능한 입력 | `400` 응답. 메시지를 그대로 보여줘도 됨 |
| `warnings` | 계산은 됐지만 결과가 의심스러움 | `200` 응답에 포함. 화면에 안내 문구로 표시 |

**`ValueError` 가 나는 경우**
```
선택된 필지가 없습니다.
면적이 있는 필지가 하나도 없습니다.
용도지역을 확인할 수 있는 필지가 없습니다.
존재하지 않는 평형입니다: 101
(감정평가액), (공시가격), (토지면적, 공시지가) 중 하나는 입력해야 합니다.
unit_mix_list 의 share 합계가 1.0 이 아닙니다: 0.9
commercial_ratio + community_ratio 는 0 이상 1 미만이어야 합니다
```

**`warnings` 에 담기는 경우**
```
용도지역이 섞여 있어 면적 가중평균을 사용했습니다
용적률 표에 없는 용도지역입니다: 자연녹지지역 (PNU)
면적이 없는 필지를 제외했습니다: PNU
조합원 수(700)가 분양 세대수(500)보다 많습니다
공급면적 합계가 지상 연면적을 초과합니다
비례율 45.2%는 통상 범위(80~120%)를 크게 벗어납니다
비례율 고정값(100.0%) 사용 : 사업비·분양가 변화가 반영되지 않습니다
```

---

## 6. 연동 확인용 스크립트

라우터 없이 엔진만 먼저 돌려 보면 경로 설정이 맞는지 확인됩니다.

```python
from calc import calc_allocation, calc_area, calc_contribution, unit_options
from schema import OwnerInput, ParcelInfo, ProjectParams, ProjectType, UnitMix
from zone import build_zone_summary

params = ProjectParams(
    name="테스트 구역", project_type=ProjectType.REDEVELOPMENT,
    site_area_m2=50_000, floor_area_ratio=250, underground_ratio=0.6,
    member_count=700, general_price_per_m2=998.25, member_price_ratio=0.8,
    unit_mix_list=[
        UnitMix("59", 59.0, 82.64, 0.31),
        UnitMix("84", 84.0, 112.40, 0.56),
        UnitMix("114", 114.0, 148.76, 0.13),
    ],
    rental_ratio=0.15, rental_supply_area_m2=59.0, rental_price_per_unit=30_000,
    commercial_ratio=0.03, community_ratio=0.05,
    housing_supply_efficiency=0.97, commercial_price_ratio=1.2,
    construction_cost_per_pyeong=850, other_cost_ratio=0.35,
    avg_prior_asset=35_000, proportional_rate=None,
)
owner = OwnerInput(desired_unit="84", official_price=35_000, appraisal_ratio=1.3)

areas = calc_area(params)
alloc = calc_allocation(params, areas)
result = calc_contribution(params, alloc, owner)
print([(u.name, u.count) for u in alloc.unit_types], alloc.rental_count)
print(result.proportional_rate, result.contribution)

zone = build_zone_summary([
    ParcelInfo("1111010100100010000", 300.0, 3_800_000, "제2종일반주거지역", "대"),
    ParcelInfo("1111010100100030000", 180.0, 5_000_000, "제3종일반주거지역", "대"),
    ParcelInfo("1111010100100040000", 120.0, 1_200_000, "제2종일반주거지역", "도로"),
])
print(zone.site_area_m2, zone.far_min, zone.far_max, zone.land_value_total)
```

**기대 출력**
```
[('59', 355), ('84', 472), ('114', 82)] 283
95.7 46233.xx
600.0 215.0 265.0 204000.0
```
- 용적률 215%는 2종(200%)과 3종(250%)의 면적 가중평균입니다.
- 종전자산 기초 204,000만원에는 지목이 "도로"인 필지가 빠져 있습니다.

---

## 7. 지금 미완성인 부분 (AI 파트에서 작업 중)

- **필지 면적·용도지역 확보 방법이 정해지지 않았습니다.** 2절 참고. 이게 연동의 가장 큰 걸림돌입니다.
- `zone.py` 의 용적률 표는 서울시 조례 기준 시작값이며, 정비사업 상향 규정은 반영돼 있지 않습니다.
- 가정치(공사비·분양가·평균 종전자산)는 임시값이라, 실제 값을 넣기 전 결과는 참고용입니다.
- 조합원 평형 선호는 "평형 비율대로 배정"으로 단순화돼 있습니다.

막히는 부분이나 응답 형태를 바꾸고 싶은 부분은 알려 주세요. 엔진 쪽에서 맞추겠습니다.
