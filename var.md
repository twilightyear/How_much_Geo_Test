# 분담금 엔진 — 백엔드에서 채워야 할 변수 목록

`AI/engine/`의 `schema.py`, `calc.py`, `zone.py`는 저장소에 있습니다.
가정치가 담긴 `wolgye1_params.py`는 gitignore라 올라가지 않았으므로, 아래 값을 백엔드에서 채워 주세요.

- 면적 단위는 **㎡**, 금액 단위는 **만원**입니다. (예외: `construction_cost_per_pyeong`은 평당, `land_price_per_m2`는 원/㎡)
- 표의 "값"은 바로 쓸 수 있는 시작값입니다. 정비계획·실거래 자료를 구하면 교체합니다.

---

## 1. ProjectParams — 구역·사업 파라미터

### 1-1. 지도에서 받아오는 값

| 변수명 | 의미 | 값 | 설명 |
|---|---|---|---|
| `site_area_m2` | 정비구역 면적(㎡) | `ZoneSummary.site_area_m2` | 선택한 필지 면적의 합계. `zone.build_zone_summary()` 결과를 그대로 넣는다 |
| `floor_area_ratio` | 용적률(%) | 슬라이더 값 | 초기값은 `ZoneSummary.far_min`, 범위는 `far_min ~ far_max` |

### 1-2. 사용자 입력

| 변수명 | 의미 | 값 | 설명 |
|---|---|---|---|
| `name` | 구역 이름 | `"사용자 지정 구역"` 등 | 표시용 문자열. 계산에는 쓰이지 않는다 |
| `project_type` | 재개발 / 재건축 | `ProjectType.REDEVELOPMENT` | 재건축이면 `ProjectType.RECONSTRUCTION`. 지금은 계산 분기 없음 |
| `member_count` | 조합원 수 | 사용자 입력 | 소유자 정보는 개인정보라 공개 API로 받을 수 없어 입력값으로 둔다 |

### 1-3. 슬라이더 (초기값을 백엔드가 지정)

| 변수명 | 의미 | 값 | 설명 |
|---|---|---|---|
| `member_price_ratio` | 조합원분양가 비율 | `0.8` (0.7~0.9) | 조합원분양가 = 일반분양가 × 이 값 |
| `other_cost_ratio` | 기타사업비 비율 | `0.35` (0.25~0.45) | 설계·금융·이주비 이자 등. 총사업비 = 공사비 × (1 + 이 값) |
| `commercial_ratio` | 상가 비율 | `0.03` (0~0.2) | 지상 연면적 중 상가가 차지하는 비율 |
| `construction_cost_per_pyeong` | 평당 공사비(만원) | `850` (700~1000) | **유일하게 평당 단위.** 엔진이 내부에서 ㎡당으로 환산한다 |
| `general_price_per_m2` | ㎡당 일반분양가(만원) | `998.25` (700~1300) | 평당 3,300만원을 환산한 값. 나중에 예측 모델이 대체 |

### 1-4. 고정 가정치 (백엔드 설정에 넣어 주세요)

| 변수명 | 의미 | 값 | 설명 |
|---|---|---|---|
| `underground_ratio` | 지하 연면적 비율 | `0.6` | 지하 연면적 ÷ 지상 연면적. 공사비 계산에 쓰인다 |
| `community_ratio` | 커뮤니티 시설 비율 | `0.05` | 주민공동시설 등. 수입이 없어 늘리면 분담금이 오른다 |
| `housing_supply_efficiency` | 공급면적 전환율 | `0.97` | 주택 연면적 → 분양 공급면적 합계 |
| `commercial_price_ratio` | 상가 분양가 배수 | `1.2` | 상가 ㎡당 분양가 = `general_price_per_m2` × 이 값 |
| `rental_ratio` | 임대 비율 | `0.15` | 전체 세대 중 임대 세대 비율 |
| `rental_supply_area_m2` | 임대 1세대 공급면적(㎡) | `59.0` | 임대는 소형 1종으로 단순화 |
| `rental_price_per_unit` | 임대 1세대 인수가(만원) | `30000` | 공공에 넘기는 가격. 종후자산에 더해진다 |
| `avg_prior_asset` | 조합원 평균 종전자산(만원) | `45000` | 임시 가정치. 비례율에 직접 영향을 준다 |
| `total_prior_asset` | 종전자산 총액(만원) | `None` | 관리처분계획이 공개되면 이 값을 넣는다. 있으면 `avg_prior_asset`보다 우선 |
| `proportional_rate` | 비례율 고정값(%) | `None` | `None`이면 사업 수지로 계산. 고정 모드일 때만 숫자(예: `100`) |

### 1-5. 평형 구성 `unit_mix_list`

| 변수명 | 의미 | 값 | 설명 |
|---|---|---|---|
| `unit_mix_list` | 평형 구성 목록 | 아래 코드 | `UnitMix` 리스트. `share` 합계는 반드시 1.0 |

```python
from schema import UnitMix

unit_mix_list = [
    UnitMix(name="59",  exclusive_area_m2=59.0,  supply_area_m2=82.64,  share=0.31),
    UnitMix(name="84",  exclusive_area_m2=84.0,  supply_area_m2=112.40, share=0.56),
    UnitMix(name="114", exclusive_area_m2=114.0, supply_area_m2=148.76, share=0.13),
]
```

| UnitMix 필드 | 의미 | 설명 |
|---|---|---|
| `name` | 평형 이름 | `OwnerInput.desired_unit`과 이 이름으로 짝지어진다 |
| `exclusive_area_m2` | 전용면적(㎡) | 평형 구분용 |
| `supply_area_m2` | 공급면적(㎡) | **분양가는 이 면적에 곱한다** |
| `share` | 분양 면적 중 비율 | 합계 1.0. 벗어나면 `ValueError` |

---

## 2. OwnerInput — 조합원 개인 입력

| 변수명 | 의미 | 값 | 설명 |
|---|---|---|---|
| `desired_unit` | 희망 평형 | `"84"` 등 | `unit_mix_list`의 `name`과 일치해야 한다. 없으면 `ValueError` |
| `appraisal_value` | 감정평가액(만원) | `None` | 감정평가 통지를 받은 경우만 입력. 있으면 최우선 사용 |
| `official_price` | 공시가격(만원) | 공시가격 API | 주택·공동주택 공시가격 |
| `land_area_m2` | 토지 지분면적(㎡) | 토지대장 | 위 두 값이 없을 때 사용 |
| `land_price_per_m2` | 개별공시지가(원/㎡) | 공시지가 API | **원 단위.** 엔진이 만원으로 환산한다 |
| `appraisal_ratio` | 감정가 보정률 | `1.3` | 감정평가액 ÷ 공시가격. 가정치이며 예측 모델이 생기면 폐기 |

종전자산 추정 우선순위: **감정평가액 > 공시가격 × 보정률 > 토지면적 × 공시지가 × 보정률**
셋 다 없으면 `ValueError`가 납니다.

---

## 3. ParcelInfo — 필지 1개 (zone.py 입력)

| 변수명 | 의미 | 값 | 설명 |
|---|---|---|---|
| `pnu` | 필지 고유번호 | V-World `pnu` | 프론트에서 선택한 필지 식별자 |
| `area_m2` | 필지 면적(㎡) | 토지특성 API | **현재 V-World 필지 응답에는 없음.** 토지특성 API를 호출하거나 폴리곤으로 계산해야 한다 |
| `land_price_per_m2` | 공시지가(원/㎡) | V-World `jiga` | 원 단위 그대로 넣는다 |
| `zoning` | 용도지역 | 토지특성 API | 예: `"제2종일반주거지역"`. 용적률 범위를 정하는 데 필요 |
| `land_category` | 지목 | 토지특성 API | 예: `"대"`, `"도로"`. 도로·구거·하천·공원·제방은 종전자산 합산에서 제외된다. 모르면 `None` |

`build_zone_summary(parcels)`가 반환하는 `ZoneSummary`:

| 변수명 | 의미 | 설명 |
|---|---|---|
| `site_area_m2` | 구역 면적 합계 | `ProjectParams.site_area_m2`로 넘긴다 |
| `far_min`, `far_max` | 용적률 범위(%) | 용적률 슬라이더의 최솟값·최댓값 |
| `land_value_total` | 종전자산 기초(만원) | Σ(면적 × 공시지가). 국공유지 제외 |
| `pnus` | 선택 필지 목록 | 기록용 |
| `warnings` | 경고 문구 | 화면에 안내로 띄운다 |

---

## 4. ⚠️ Allocation — 아직 자동 계산되지 않음

`calc_project`와 `calc_contribution`은 `Allocation`(세대수 배분)을 인자로 받습니다.
**연면적에서 세대수를 자동 계산하는 로직이 아직 없어서, 지금은 호출하는 쪽이 직접 만들어 넘겨야 합니다.**

| 변수명 | 의미 | 설명 |
|---|---|---|
| `unit_types` | 평형별 세대수 | `UnitType(name, exclusive_area_m2, supply_area_m2, count)` 리스트 |
| `rental_count` | 임대 세대수 | 정수 |
| `sale_supply_m2` | 분양 공급면적 합계(㎡) | 현재 계산에는 쓰이지 않음. 0을 넣어도 동작 |

```python
from calc import Allocation
from schema import UnitType

alloc = Allocation(
    unit_types=[
        UnitType("59",  59.0,  82.64,  450),
        UnitType("84",  84.0,  112.40, 600),
        UnitType("114", 114.0, 148.76, 100),
    ],
    rental_count=200,
    sale_supply_m2=450 * 82.64 + 600 * 112.40 + 100 * 148.76,
)
```

이 부분은 `calc_allocation(params, areas)` 한 줄로 바뀔 예정입니다.
**그때 호출 방식이 달라지니, 연동 코드에서 이 부분만 따로 떼어 두시면 수정이 쉽습니다.**

---

## 5. 호출 예시

```python
from calc import Allocation, calc_contribution
from schema import OwnerInput, ProjectParams, ProjectType, UnitMix, UnitType
from zone import build_zone_summary

zone = build_zone_summary(parcels)            # ParcelInfo 리스트 → 구역 집계

params = ProjectParams(
    name="사용자 지정 구역",
    project_type=ProjectType.REDEVELOPMENT,
    site_area_m2=zone.site_area_m2,
    floor_area_ratio=zone.far_min,            # 슬라이더 값
    underground_ratio=0.6,
    member_count=900,
    general_price_per_m2=998.25,
    member_price_ratio=0.8,
    unit_mix_list=unit_mix_list,
    rental_ratio=0.15,
    rental_supply_area_m2=59.0,
    rental_price_per_unit=30000,
    commercial_ratio=0.03,
    community_ratio=0.05,
    housing_supply_efficiency=0.97,
    commercial_price_ratio=1.2,
    construction_cost_per_pyeong=850,
    other_cost_ratio=0.35,
    avg_prior_asset=45000,
)

owner = OwnerInput(desired_unit="84", official_price=35000, appraisal_ratio=1.3)
result = calc_contribution(params, alloc, owner)
```

응답으로 쓸 값:

| 변수명 | 의미 |
|---|---|
| `result.contribution` | 분담금(만원). 음수면 환급 |
| `result.right_value` | 권리가액 |
| `result.member_price` | 조합원분양가 |
| `result.prior_asset` | 추정 종전자산 |
| `result.project.proportional_rate` | 비례율(%) |
| `result.project.rate_fixed` | 비례율이 고정값인지 여부 |
| `result.project.total_cost` | 총사업비 |
| `result.project.total_post_asset` | 종후자산 총액 |
| `result.project.warnings` | 경고 문구 목록. 화면에 그대로 띄우면 된다 |

---

## 6. 연동 확인용 기준값

조건: 위 예시 파라미터에서 `commercial_ratio=0.0`, 세대수 450/600/100, 임대 200세대, 공시가 3.5억이 84형 희망

| 항목 | 값 |
|---|---|
| 총사업비 | 6,942 억 |
| 종후자산 | 10,662 억 |
| 비례율 | 91.8 % |
| 권리가액 | 41,792 만원 |
| 조합원분양가 | 89,763 만원 |
| **분담금** | **47,971 만원** |

이 값이 나오면 연동이 제대로 된 것입니다.

> 참고: 이 조건에서는 "공급면적 합계가 지상 연면적을 초과합니다" 경고가 뜹니다.
> 검증용 세대수를 옛 기준으로 직접 넣어서 생기는 것으로, 세대수 자동 배분이 들어가면 사라집니다.

---

## 7. 주의사항

- **`float | None` 문법을 쓰므로 Python 3.10 이상**이어야 합니다. Docker 이미지 버전을 확인해 주세요.
- `ProjectParams`는 **키워드 인자로만** 생성할 수 있습니다. `ProjectParams("이름", ...)`처럼 위치 인자로는 안 됩니다.
- 잘못된 값은 생성 시점에 `ValueError`가 납니다. `share` 합계 ≠ 1.0, `rental_ratio` 0~1 밖, `commercial_ratio + community_ratio` ≥ 1, 종전자산 총액·평균 둘 다 없음.
- `zone.py`의 용적률 표(`FAR_TABLE`)는 서울시 조례 기준으로 잡은 **시작값**이며 정비사업 상향 규정이 반영되지 않았습니다. 확인 후 교체 예정입니다.
- V-World가 주는 용도지역 문자열이 `FAR_TABLE`의 키와 다르면 경고만 뜨고 그 필지는 용적률 계산에서 빠집니다. 실제 응답 문자열을 한 번 확인해 주세요.
