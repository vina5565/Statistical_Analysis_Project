# COVID-19 대학입시 영향 분석 프로젝트 실행 가이드

## 📋 프로젝트 개요
69개의 생활기록부 txt 파일을 분석하여 코로나19가 고교 내신·학생부·대학전형에 미친 영향을 통계적으로 검증

## 🎯 분석 목표
- **H1-1**: 코로나 코호트의 성적 변동성 증가 검증
- **H1-2**: 세특 텍스트 변화(탐구/실험 → 온라인/원격)의 매개효과 분석
- **H1-3**: 대학 전형요강의 정성평가 강조 변화 분석

## 📁 파일 구조
```
project/
├── step1_parse_all_files.py          # 1단계: 전체 파일 파싱
├── step2_exploratory_analysis.py     # 2단계: 탐색적 데이터 분석
├── step3_hypothesis_testing.py       # 3단계: 가설 검증
├── step4_visualization.py            # 4단계: 시각화 생성
├── step5_generate_reports.py         # 5단계: 보고서 생성
├── utils/
│   ├── parser.py                     # 파싱 유틸리티
│   ├── statistical_tests.py         # 통계 검정 함수
│   └── visualization_utils.py       # 시각화 함수
├── data/
│   ├── raw/                          # 원본 txt 파일 (69개)
│   ├── processed/                    # 처리된 데이터
│   │   ├── student_info.csv
│   │   ├── grades.csv
│   │   ├── seteuk.csv
│   │   └── volatility.csv
│   └── results/                      # 분석 결과
│       ├── hypothesis_tests.csv
│       └── statistics.csv
└── outputs/
    ├── figures/                      # 시각화 결과
    ├── reports/                      # 개별 학생 리포트
    └── final_report.pdf              # 최종 종합 보고서
```

## 🚀 실행 순서

### STEP 1: 전체 파일 파싱 (약 5-10분 소요)
```bash
python step1_parse_all_files.py
```
- 입력: data/raw/*.txt (69개 파일)
- 출력: data/processed/*.csv (학생정보, 성적, 세특, 변동성)

### STEP 2: 탐색적 데이터 분석 (약 2-3분 소요)
```bash
python step2_exploratory_analysis.py
```
- 입력: data/processed/*.csv
- 출력: 기술통계량, 상관관계, 분포 그래프

### STEP 3: 가설 검증 (약 3-5분 소요)
```bash
python step3_hypothesis_testing.py
```
- 입력: data/processed/*.csv
- 출력: 통계 검정 결과 (t-test, regression, mediation)

### STEP 4: 시각화 생성 (약 2-3분 소요)
```bash
python step4_visualization.py
```
- 입력: data/processed/*.csv, data/results/*.csv
- 출력: outputs/figures/*.png (20-30개 그래프)

### STEP 5: 보고서 생성 (약 5-10분 소요)
```bash
python step5_generate_reports.py
```
- 입력: 모든 데이터 및 결과
- 출력: outputs/reports/ (69개 개별 리포트 + 1개 종합 리포트)

## 📊 주요 분석 지표

### 1. 성적 변동성 (Grade Volatility)
- 전체 표준편차 (overall_volatility)
- 교과군별 표준편차
- 학기별 변화량 평균 (grade_change_mean)
- 변동계수 (CV: Coefficient of Variation)

### 2. 세특 키워드 빈도
- 탐구/실험 키워드: 실험, 탐구, 관찰, 측정, 프로젝트 등
- 온라인/원격 키워드: 온라인, 원격, 비대면, 화상 등
- 빈도 측정: 1000자당 키워드 출현 횟수

### 3. 코호트 분류
- **Pre-COVID**: 2018-2020 졸업 (admission_year 2015-2017)
- **COVID**: 2021-2024 졸업 (admission_year 2018-2021)

## 🔧 설치 필요 패키지
```bash
pip install pandas numpy scipy statsmodels matplotlib seaborn plotly scikit-learn python-docx openpyxl --break-system-packages
```

## ⚠️ 주의사항

1. **파일명 규칙 확인**
   - 파일명 형식: `{학번}_3학년_{학과}_{이름}_{전형}_censored.txt`
   - 학번 9자리 (예: 202110937)

2. **인코딩 문제**
   - 모든 파일이 UTF-8 인코딩인지 확인
   - 필요시 `iconv`로 변환

3. **메모리 관리**
   - 69개 파일 처리 시 약 1-2GB RAM 사용
   - 메모리 부족 시 배치 처리로 전환

4. **데이터 품질 체크**
   - 파싱 실패 파일 로그 확인
   - 성적/세특 누락 케이스 검토

## 📈 예상 결과물

1. **데이터셋**
   - student_info.csv: 69행 × 8열
   - grades.csv: ~1,500-2,000행 × 12열
   - seteuk.csv: ~800-1,000행 × 10열
   - volatility.csv: 69행 × 15열

2. **통계 검정 결과**
   - H1-1: t-test, Levene's test, regression 결과
   - H1-2: Mediation analysis 결과
   - H1-3: 키워드 빈도 비교 결과

3. **시각화**
   - 성적 분포 비교 그래프
   - 변동성 트렌드 그래프
   - 키워드 빈도 변화 그래프
   - 교과군별 분석 그래프

4. **보고서**
   - 개별 학생 리포트 69개 (PDF/DOCX)
   - 종합 분석 리포트 1개 (PDF/DOCX)

## 🐛 트러블슈팅

### 문제 1: 파싱 실패
```bash
# 로그 확인
cat logs/parsing_errors.log

# 특정 파일 개별 테스트
python -c "from utils.parser import SchoolRecordParser; parser = SchoolRecordParser(); result = parser.parse_file('data/raw/파일명.txt'); print(result)"
```

### 문제 2: 통계 검정 오류
```bash
# 데이터 무결성 확인
python -c "import pandas as pd; df = pd.read_csv('data/processed/grades.csv'); print(df.describe()); print(df.isnull().sum())"
```

### 문제 3: 메모리 부족
```python
# step1_parse_all_files.py 수정
# 배치 크기 조정: BATCH_SIZE = 10 으로 변경
```

## 📞 문의사항
코드 실행 중 문제 발생 시 에러 메시지와 함께 문의하세요.