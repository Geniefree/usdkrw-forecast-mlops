# USD/KRW 환율 예측 MLOps 구현

> 글로벌 금융시장 데이터 기반 실시간 환율 방향 예측 시스템

고려대학교 데이터애널리틱스특수연구 팀 프로젝트 (6인)

---

## 프로젝트 개요

시중 환율 정보는 수 분~수십 분 지연되며, 글로벌 시장 변수를 실시간으로 반영하지 못한다는 한계가 있었습니다.  
이를 해결하기 위해 BTC, JPY, WTI, GOLD, DXY 등 6종 글로벌 금융자산 데이터를 1분 단위로 수집하고,  
RandomForest 기반 환율 방향 예측 모델과 자동화 파이프라인을 구축하였습니다.

---

## 시스템 구조

```
yfinance API (1분봉)
    ↓
데이터 수집 · 전처리 (src/preprocess.py)
    ↓
PostgreSQL 저장 (marketdb.latest_24h_market_data_1m)
    ↓
RandomForest 예측 모델 (FastAPI)
    ↓
Dash 실시간 대시보드
```

---

## 수집 데이터

| Ticker | 자산 | 역할 |
|--------|------|------|
| KRW=X | USD/KRW | 예측 타겟 |
| BTC-USD | 비트코인 | 위험선호도 지표 |
| JPY=X | 엔화 | 아시아 통화 연동 |
| CL=F | WTI 원유 | 원자재·달러 연동 |
| GC=F | 금 | 안전자산 지표 |
| DX-Y.NYB | 달러인덱스 | 달러 강도 지표 |

---

## 내 담당 파트

- **데이터 수집 파이프라인 설계** — yfinance API 기반 6종 자산 1분봉 실시간 수집
- **전처리 파이프라인 구현** (`src/preprocess.py`)
  - UTC timestamp 정렬 및 Rolling Window 기반 공통 인덱스 생성
  - 주말·공휴일 비활성 구간 제외 (금요일 22:00 UTC ~ 일요일 22:00 UTC)
  - 소규모 갭 선형 보간 적용
- **PostgreSQL 데이터 저장소 구축** — CSV 및 DB 자동 적재
- **GitHub 협업 환경 구성** — 팀 버전관리 환경 설정

---

## 실행 방법

### 사전 준비

```bash
# 패키지 설치
pip install -r requirements.txt

# Docker로 PostgreSQL 실행
docker-compose up -d
```

### 데이터 수집 · 전처리 실행

```bash
python3 src/preprocess.py
```

실행 시 자동으로 수행되는 작업:
1. 최근 24시간 1분봉 데이터 수집
2. UTC timestamp 정렬
3. 비활성 구간 제외 후 최근 유효 1440분 생성
4. 선형 보간 적용
5. CSV 저장 → PostgreSQL 적재

---

## 출력

| 형식 | 경로 / 위치 |
|------|------------|
| CSV | `data/processed/market_data_1m_24h_interpolated.csv` |
| PostgreSQL | `marketdb.latest_24h_market_data_1m` |

DB 연결: `postgresql://admin:admin@localhost:5432/marketdb`

---

## 프로젝트 구조

```
usdkrw-forecast-mlops/
├── src/
│   └── preprocess.py       # 데이터 수집·전처리 파이프라인
├── notebooks/              # 모델 실험 노트북
├── data/
│   └── processed/          # 전처리된 데이터
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 기술 스택

`Python` `yfinance` `PostgreSQL` `Docker` `FastAPI` `Dash` `RandomForest` `pandas`

---

## 포트폴리오

→ [프로젝트 상세 페이지](https://geniefree.github.io/projects/mlops.html)
