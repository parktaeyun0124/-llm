# 🎨 Local Image Studio · SDXL-Turbo

> **로컬에서 돌아가는 이미지 생성 웹앱.** FastAPI 백엔드 하나가 SDXL-Turbo 파이프라인 + 정적 UI를 동시에 서빙합니다.

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/parktaeyun0124/-llm@main/preview.png" alt="Local Image Studio Preview" width="900">
</p>

---

## 📌 프로젝트 개요

이 프로젝트는 4B 이하 경량 이미지 생성 모델(**SDXL-Turbo, 3.5B**)을 가장 단순한 방식으로 웹 UI에 연결한 예제입니다.

- **Backend (FastAPI + diffusers)** : 앱 시작 시 Hugging Face `diffusers` 파이프라인을 1회 로드, `/api/generate`로 프롬프트 → PNG(base64) 반환.
- **Frontend (Vanilla HTML/CSS/JS)** : 별도 빌드 없이 `index.html` 한 파일. 글래스모피즘 다크 UI.
- **Runtime** : CUDA / Apple Silicon(MPS) / CPU 자동 감지. M 시리즈 맥에서 GPU 가속 그대로 사용.

---

## 🌟 주요 기능

| 기능 | 설명 |
|------|------|
| ⚡ **1–4 step 생성** | SDXL-Turbo는 distillation으로 step 수를 극단적으로 줄임. RTX/M 시리즈에서 수 초 내 출력 |
| 🧠 **자동 디바이스 선택** | CUDA → MPS → CPU 순으로 자동 선택, fp16/fp32도 자동 |
| 🎛 **Steps · Seed 컨트롤** | 슬라이더로 step(1–8), seed 지정 가능(비우면 랜덤) |
| 🎨 **Premium UI** | 글래스모피즘 + 그라디언트 + Lucide Icons + 부드러운 페이드인 |
| 🛡 **첫 1회만 다운로드** | HuggingFace 캐시(`~/.cache/huggingface/`)에 저장 후 오프라인 가능 |
| 🌐 **CORS 허용** | `allow_origins=["*"]` |

---

## 🛠 기술 스택

### Backend
- **Python 3.11+**
- **FastAPI** — 비동기 REST API
- **Uvicorn** — ASGI 서버
- **diffusers / transformers / accelerate** — Hugging Face 이미지 생성 파이프라인
- **torch** — CUDA / MPS / CPU 백엔드

### Frontend
- **Vanilla HTML/CSS/JS**
- **Lucide Icons** — SVG 아이콘

### Model
- **stabilityai/sdxl-turbo** — 3.5B params, 1–4 step distilled SDXL
- 라이선스: **Stability AI Non-Commercial Community License** (상업 사용 시 별도 라이선스 필요)

---

## 🚀 시작하기

### 1. 사전 준비

| 도구 | 설치 |
|------|------|
| Python 3.11+ | <https://www.python.org/downloads/> |
| 디스크 여유 공간 | **약 15GB** (모델 ~13GB + 라이브러리) |
| (선택) GPU | CUDA GPU 또는 Apple Silicon M 시리즈 추천 |

### 2. 클론 & 의존성 설치

```bash
git clone https://github.com/parktaeyun0124/-llm.git
cd -llm

# (권장) 가상환경
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

> ⚠️ **첫 실행은 모델을 약 13GB 다운로드합니다 (10–30분, 인터넷 속도 따라).**
> 두 번째 실행부터는 HuggingFace 캐시에서 즉시 로드됩니다.

브라우저:
```
http://localhost:8000
```

프롬프트 입력 → Generate.

---

## 🔌 API 명세

| Method | Path | 설명 | 응답 |
|--------|------|------|------|
| `GET`  | `/`            | 이미지 생성 UI 반환 | `text/html` |
| `GET`  | `/api/info`    | 로드된 모델·디바이스 | `application/json` |
| `POST` | `/api/generate`| 프롬프트 → 이미지 | `application/json` (PNG base64) |

### `POST /api/generate` 요청 예시
```json
{
  "prompt": "a cinematic photo of a fox in autumn forest, golden hour, 35mm",
  "steps": 2,
  "seed": 42
}
```

| 필드 | 타입 | 기본 | 설명 |
|------|------|------|------|
| `prompt` | string (1–2000) | 필수 | 텍스트 프롬프트 |
| `steps`  | int (1–8) | `2` | inference step 수. SDXL-Turbo는 1–4가 권장 |
| `seed`   | int / null | `null` | 지정 시 결과 재현 가능, 없으면 랜덤 |

### 응답 예시
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",  // PNG, base64
  "prompt": "a cinematic photo of a fox...",
  "steps": 2,
  "seed": 42
}
```

---

## 📁 프로젝트 구조

```
.
├── main.py            # FastAPI 진입점 — 디바이스 감지 + diffusers 로드 + /api/generate
├── index.html         # 단일 파일 프론트엔드 (CSS·JS 인라인)
├── requirements.txt   # Python 의존성
├── preview.png        # README용 스크린샷
└── README.md
```

### main.py 핵심 흐름

```
[startup]
  ├─ pick_device()         CUDA / MPS / CPU 자동 선택
  └─ from_pretrained()     SDXL-Turbo 파이프라인 로드 (첫 실행 시 다운로드)

[runtime]
  브라우저 ──▶ FastAPI /api/generate ──▶ pipe(prompt, steps, guidance_scale=0.0)
     ▲                                       │
     └──── PNG base64 응답 ◀── PIL → BytesIO ─┘
```

---

## 🎨 UI 포인트

- **컬러 팔레트** : `#0f172a` 베이스 + `#3b82f6`(블루) / `#a78bfa`(퍼플) 그라디언트
- **글래스모피즘** : `backdrop-filter: blur(12px)` + 반투명 카드
- **컨트롤** : Steps 슬라이더 / Seed 숫자 입력 / Enter 키로 즉시 생성
- **로딩 상태** : 스피너 + 메시지, 완료 시 페이드인 애니메이션

---

## 🧪 빠른 테스트

서버 띄운 뒤 별도 터미널:

```bash
# 모델/디바이스 확인
curl http://localhost:8000/api/info

# 이미지 생성 (PNG는 base64로 옴 — 파일로 저장하려면 jq + base64 디코딩)
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"a futuristic city skyline at sunset","steps":2}' \
  | python -c "import sys,json,base64; open('out.png','wb').write(base64.b64decode(json.load(sys.stdin)['image']))"
```

---

## 🐛 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| 첫 실행이 매우 느림 | 정상. 모델 13GB를 다운로드 중. 진행 상황은 터미널 로그 확인 |
| `OutOfMemoryError` (GPU) | VRAM 부족. `MODEL_ID=stabilityai/sd-turbo` 환경변수로 0.86B 경량판 사용 |
| Apple Silicon에서 검은 이미지만 나옴 | MPS+fp16 VAE 버그. 코드에 `upcast_vae()` 처리됨. 그래도 발생 시 `torch>=2.1`로 업그레이드 |
| `HuggingFace ... ConnectionError` | 학교/회사망 차단 가능성. 다른 네트워크에서 1회 받아두면 캐시 재사용됨 |
| UI에 "백엔드 연결 실패" | FastAPI(8000) 실행 여부 확인 |
| CORS 에러 | `main.py`의 `allow_origins`에 도메인 추가 |

---

## 🔁 모델 갈아끼우기

환경변수 `MODEL_ID`로 다른 diffusers 호환 모델 지정 가능:

```bash
# 더 가벼운 0.86B 버전
MODEL_ID=stabilityai/sd-turbo python -m uvicorn main:app --port 8000

# 클래식 SD 1.5 (상업 사용 가능, Open RAIL)
MODEL_ID=runwayml/stable-diffusion-v1-5 python -m uvicorn main:app --port 8000
```

> ⚠ SD 1.5는 step 25–50 / guidance 7.5가 표준이라 현재 코드의 `guidance_scale=0.0` 기본값은 Turbo 계열 전용입니다. SD 1.5로 갈아끼울 거면 `main.py`의 `guidance_scale`을 7.5로, `steps` 슬라이더 max를 50으로 올려주세요.

---

## 🗺 향후 개선 아이디어

- [ ] 생성 이미지 히스토리 (IndexedDB)
- [ ] negative prompt / aspect ratio 컨트롤
- [ ] 진행률 스트리밍 (step 단위 callback)
- [ ] Docker 이미지 배포
- [ ] img2img / inpaint 지원

---

## 📝 라이선스

- 이 레포의 **코드** : MIT
- **모델 가중치**(SDXL-Turbo) : [Stability AI Non-Commercial Community License](https://huggingface.co/stabilityai/sdxl-turbo/blob/main/LICENSE.md) — 연구/개인용 OK, 상업 사용 시 별도 라이선스 필요
