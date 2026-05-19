---
title: Local Image Studio
emoji: 🎨
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: SD-Turbo 이미지 생성 웹앱 (FastAPI + 글래스모피즘 UI)
---

# 🎨 Local Image Studio · SD-Turbo

> **HuggingFace Spaces에서 무료로 돌아가는 이미지 생성 웹앱.** FastAPI 백엔드 하나가 SD-Turbo 파이프라인 + 정적 UI를 동시에 서빙합니다.

<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/parktaeyun0124/-llm@main/preview.png" alt="Local Image Studio Preview" width="900">
</p>

---

## 📌 프로젝트 개요

이 프로젝트는 경량 이미지 생성 모델(**SD-Turbo, 0.86B**)을 가장 단순한 방식으로 웹 UI에 연결한 예제입니다.
HuggingFace Spaces의 **CPU basic (16GB RAM, 무료)** 티어에서 영구 실행을 목표로 합니다.

- **Backend (FastAPI + diffusers)** : 앱 시작 시 Hugging Face `diffusers` 파이프라인을 1회 로드, `/api/generate`로 프롬프트 → PNG(base64) 반환.
- **Frontend (Vanilla HTML/CSS/JS)** : 별도 빌드 없이 `index.html` 한 파일. 글래스모피즘 다크 UI.
- **Runtime** : CUDA / Apple Silicon(MPS) / CPU 자동 감지. HF Spaces CPU basic에서는 CPU fp32로 동작.
- **Deploy** : Docker 이미지로 빌드 → HF Space에서 자동 서빙.

---

## 🌟 주요 기능

| 기능 | 설명 |
|------|------|
| ⚡ **1–4 step 생성** | SD-Turbo는 distillation으로 step 수를 극단적으로 줄임. CPU에서도 수십 초 ~ 1~2분 내 출력 |
| 🧠 **자동 디바이스 선택** | CUDA → MPS → CPU 순으로 자동 선택, fp16/fp32도 자동 |
| 🎛 **Steps · Seed 컨트롤** | 슬라이더로 step(1–8), seed 지정 가능(비우면 랜덤) |
| 🎨 **Premium UI** | 글래스모피즘 + 그라디언트 + Lucide Icons + 부드러운 페이드인 |
| 🛡 **첫 1회만 다운로드** | HuggingFace 캐시에 저장 후 동일 인스턴스에서 재로드 |
| 🌐 **CORS 허용** | `allow_origins=["*"]` |

---

## 🛠 기술 스택

### Backend
- **Python 3.11+**
- **FastAPI** — 비동기 REST API
- **Uvicorn** — ASGI 서버
- **diffusers / transformers / accelerate** — Hugging Face 이미지 생성 파이프라인
- **torch (CPU wheel)** — HF Spaces CPU basic 환경 가정

### Frontend
- **Vanilla HTML/CSS/JS**
- **Lucide Icons** — SVG 아이콘

### Model
- **stabilityai/sd-turbo** — 0.86B params, 1–4 step distilled SD
- 라이선스: **Stability AI Non-Commercial Community License** (상업 사용 시 별도 라이선스 필요)

### Deploy
- **HuggingFace Spaces (Docker SDK)** — CPU basic, 무료, 영구 실행 (48h 비활성 시 sleep)
- **포트** : 7860 (HF Spaces 표준)

---

## 🚀 로컬 실행

### 1. 사전 준비

| 도구 | 설치 |
|------|------|
| Python 3.11+ | <https://www.python.org/downloads/> |
| 디스크 여유 공간 | **약 5GB** (모델 ~2.3GB + 라이브러리) |
| (선택) GPU | CUDA GPU 또는 Apple Silicon M 시리즈 추천 |

### 2. 클론 & 의존성 설치

```bash
git clone https://github.com/parktaeyun0124/-llm.git
cd -llm

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
# 로컬에서는 GPU 환경에 맞게 torch 별도 설치 (HF Spaces용 Dockerfile에는 CPU wheel 이미 명시)
pip install torch>=2.1
```

### 3. 서버 실행

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

> ⚠️ **첫 실행은 모델을 약 2.3GB 다운로드합니다.**

브라우저:
```
http://localhost:8000
```

---

## 🐳 Docker로 실행

```bash
docker build -t image-studio .
docker run --rm -p 7860:7860 image-studio
# http://localhost:7860
```

---

## ☁️ HuggingFace Spaces 배포

### 자동 (HF Space에 git push)

1. HF 계정에서 **New Space** 생성 → **Docker** SDK, **CPU basic** 선택
2. 로컬에서:
   ```bash
   git remote add space https://huggingface.co/spaces/<USERNAME>/<SPACE_NAME>
   git push space master:main
   ```
3. HF가 자동으로 Docker 이미지 빌드 → 10~20분 후 라이브
4. 첫 추론 요청 시 모델 다운로드 추가로 5~10분 소요 (캐시 후 즉시 로드)

### 자원 사용량 (CPU basic 기준)

| 항목 | 값 |
|------|----|
| RAM | ~3~4 GB 사용 / 16 GB 한도 |
| 디스크 | ~3 GB / 50 GB |
| 1장 생성 시간 | 30s ~ 2분 (CPU, 2 step, 512×512) |

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
| `steps`  | int (1–8) | `2` | inference step 수. Turbo는 1–4 권장 |
| `seed`   | int / null | `null` | 지정 시 결과 재현 가능, 없으면 랜덤 |

### 응답 예시
```json
{
  "image": "iVBORw0KGgoAAAANSUhEUgAA...",
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
├── Dockerfile         # HF Spaces (port 7860) 배포용 컨테이너 정의
├── requirements.txt   # Python 의존성 (torch는 Dockerfile에서 CPU wheel 별도 설치)
├── preview.png        # README용 스크린샷
└── README.md          # HF Spaces frontmatter 포함
```

---

## 🔁 모델 갈아끼우기

환경변수 `MODEL_ID`로 다른 diffusers 호환 모델 지정 가능:

```bash
# SDXL-Turbo (3.5B, ~13GB) — GPU 환경 권장. HF Spaces CPU basic에서는 동작 어려움
MODEL_ID=stabilityai/sdxl-turbo python -m uvicorn main:app --port 8000

# 더 가벼운 distilled SD 계열
MODEL_ID=segmind/tiny-sd python -m uvicorn main:app --port 8000
```

> ⚠ Turbo 계열이 아닌 모델로 갈아끼우면 `guidance_scale=0.0`을 7.5 등으로 조정해야 정상적인 이미지가 나옵니다.

---

## 🐛 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| HF Space 빌드 실패 | 보통 torch 다운로드 타임아웃. 재시도 또는 Settings → Factory rebuild |
| 첫 응답이 매우 느림 | 정상. CPU에서 SD-Turbo는 30초~2분 소요 |
| 모델 캐시 안 잡힘 | HF Spaces persistent storage 미설정 시 재시작마다 다운로드. 무료 티어에서는 그대로 수용 |
| UI에 "백엔드 연결 실패" | FastAPI 프로세스가 죽음. Space Logs 확인 |
| 한국어 프롬프트 결과가 어색 | SD 계열은 영어 학습 비중이 압도적. 영어 프롬프트 권장 |

---

## 📝 라이선스

- 이 레포의 **코드** : MIT
- **모델 가중치**(SD-Turbo) : [Stability AI Non-Commercial Community License](https://huggingface.co/stabilityai/sd-turbo/blob/main/LICENSE) — 연구/개인용 OK, 상업 사용 시 별도 라이선스 필요
