# NewsEye (뉴스아이) 👁️🛡️

> **AI 및 지식 그래프 기반 지능형 IT 범죄 위협 인텔리전스 플랫폼**

NewsEye는 실시간 뉴스 데이터를 수집하여 AI(KoBERT, LLM)로 분석하고, 위협 개체 간의 관계를 지식 그래프(Neo4j)로 시각화하며, 사용자 자산 맞춤형 위협 경보(EASM)를 제공하는 상용 수준의 보안 솔루션입니다.

---

## ✨ 핵심 차별점 (Core Features)

### 1. 지능형 다차원 분석 (AI-Powered Analysis)
- **KoBERT 범죄 분류**: 7대 IT 범죄 유형(피싱, 랜섬웨어 등) 자동 분류.
- **한국어 특화 NLP**: `Leo97/KoELECTRA` 모델을 활용하여 뉴스 본문에서 공격자(Actor), 대상(Target), 위치(Location) 엔티티를 정밀 추출.
- **LLM 기반 인사이트**: 뉴스 요약 및 즉각적인 대응 가이드(Actionable Insights) 자동 생성.

### 2. 위협 지식 그래프 (Knowledge Graph)
- **Neo4j 기반 시각화**: `공격자 - 취약점(CVE) - 피해기관 - 범죄유형` 간의 복잡한 관계를 지식 그래프로 구조화.
- **인터랙티브 드릴다운**: 그래프 노드 클릭 시 연관된 모든 뉴스와 위협 지표를 즉시 분석하는 심층 탐색 기능.

### 3. 실시간 OSINT 위협 보강 (OSINT Enrichment)
- **실시간 평판 조회**: 뉴스 내 IP, 도메인, 해시를 **VirusTotal** 및 **AbuseIPDB**와 연동하여 실시간 악성 여부 검증.
- **API 절약 모드**: 리스크 점수 기반의 선택적 조회 및 메모리 캐싱으로 효율적인 API 운영 지원.

### 4. 사용자 맞춤형 공격 표면 관리 (EASM & Alert)
- **자산 기반 타겟팅 경보**: 사용자가 등록한 기술 스택(예: Windows, AWS)과 위협 정보를 매칭하여 **최상위 긴급 경보(Targeted Alert)** 발송.
- **WebSocket 실시간 알림**: 시스템 가동 중 새로운 위협 탐지 시 대시보드에 즉각적인 시각적 피드백 제공.

---

## 💾 데이터셋 가이드 (Dataset Guide)

본 프로젝트는 약 17만 건의 대규모 뉴스 데이터를 다룹니다. GitHub 용량 제한으로 인해 전체 데이터 대신 구조 파악을 위한 **샘플 데이터**만 포함되어 있습니다.

### 1. 샘플 데이터 (Sample Data)
- 위치: `data/processed/sample_news_dataset.csv`
- 내용: 전체 데이터셋의 상위 100개 레코드를 포함하고 있어, 데이터 구조(컬럼)를 즉시 확인할 수 있습니다.

### 2. 전체 데이터셋 다운로드 (Full Dataset Download)
- 전체 데이터가 필요하신 경우 아래 링크를 통해 다운로드하여 `data/` 폴더에 압축을 풀어주세요.
- **[구글 드라이브 다운로드 링크](https://drive.google.com/file/d/1UyDVIx2OeWN_Xo9CcEt77IAYstnKmI4G/view?usp=sharing)**

---

## 🏗️ 시스템 아키텍처 (Architecture)
<img width="1693" height="929" alt="Image" src="https://github.com/user-attachments/assets/6165b2cf-ccfd-4577-890d-dd6b709b102b" />


---

## 🚀 One-Click 실행 가이드 (Docker Compose)

Docker가 설치되어 있다면 단 한 줄의 명령어로 전체 시스템(DB, 그래프, 백엔드, 프론트엔드, 크롤러)을 구동할 수 있습니다.

```bash
# 전체 시스템 빌드 및 실행
docker-compose up --build -d
```

- **대시보드**: `http://localhost:3000`
- **API 문서**: `http://localhost:8000/docs`
- **Neo4j 브라우저**: `http://localhost:7474` (ID/PW: neo4j/password)

---

## 🛠️ 수동 설치 및 실행 (Development)

### 1. 백엔드 설정
```bash
cd newseye-backend
cp .env.example .env  # API 키 및 DB 정보 설정
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 2. 프론트엔드 설정
```bash
cd newseye-frontend
npm install
npm start
```

### 3. 크롤러 및 ML 실행
```bash
cd newseye-news-crawler
pip install -r requirements.txt
python simple_crawler.py
```

---

## 📊 기술 스택 (Tech Stack)

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis, Neo4j, ChromaDB
- **Frontend**: React 18, Recharts, React Force Graph, Tailwind CSS(Custom)
- **AI/ML**: PyTorch, Transformers (KoBERT, KoELECTRA), Facebook Prophet
- **Data**: Scrapy, feedparser, OSINT APIs (VirusTotal, AbuseIPDB)

---

*NewsEye — 차세대 AI 기술로 사이버 위협의 '눈'이 되어 드립니다.*
