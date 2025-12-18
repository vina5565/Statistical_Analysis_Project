#!/bin/bash
# 전체 파이프라인 실행 스크립트

# =================================================================
# 파이썬 순차 실행 스크립트 (run_analysis.sh)
#
# 이 스크립트는 'step1~.py'부터 'step5~.py'까지의 파이썬 파일을
# 순서대로 실행하며, 각 단계의 성공/실패 여부를 확인합니다.
#
# WSL (Ubuntu) 환경에서 가상 환경을 사용하도록 설정되었습니다.
#
# 사용법:
# 1. 파일에 실행 권한 부여: chmod +x run_analysis.sh
# 2. 스크립트 실행: ./run_analysis.sh
# =================================================================

# ---------------------------------
# 1. 파이썬 가상 환경 활성화 (필수)
# ---------------------------------

# 가상 환경 폴더명
VENV_NAME="final_project"

# WSL/Linux 환경에서 가상 환경을 활성화합니다.
# 이 명령은 스크립트가 실행되는 동안 VENV의 python 경로를 사용하도록 설정합니다.
echo "가상 환경 ($VENV_NAME) 활성화 중..."
source "bin/activate"

# 가상 환경 활성화 실패 시 오류 처리
if [ $? -ne 0 ]; then
    echo "[ERROR] 가상 환경 '$VENV_NAME' 활성화에 실패했습니다."
    echo "가상 환경 폴더명이나 경로(./$VENV_NAME/bin/activate)를 확인해 주세요."
    exit 1
fi
echo "✓ 가상 환경 활성화 성공. 파이썬 스크립트가 가상 환경에서 실행됩니다."


# 실행할 파이썬 인터프리터를 지정합니다. 가상 환경이 활성화되었으므로 "python"만 사용해도 됩니다.
PYTHON_CMD="python"

# ---------------------------------
# 2. 순차적 파이썬 스크립트 실행 및 에러 확인
# ---------------------------------

echo "================================================================================"
echo "COVID-19 대학입시 영향 분석 파이프라인"
echo "================================================================================"

# Step 1: 파싱
echo ""
echo "[1/4] Step 1: 생활기록부 파싱 중..."
python step1_parse_all_files.py

if [ $? -ne 0 ]; then
    echo "❌ Step 1 실패"
    exit 1
fi

# Step 2: EDA
echo ""
echo "[2/4] Step 2: 탐색적 분석 중..."
python step2_exploratory_analysis.py

if [ $? -ne 0 ]; then
    echo "❌ Step 2 실패"
    exit 1
fi

# Step 3: 가설 검증
echo ""
echo "[3/4] Step 3: 가설 검증 중..."
python step3_hypothesis_testing.py

if [ $? -ne 0 ]; then
    echo "❌ Step 3 실패"
    exit 1
fi

# Step 4: 시각화
echo ""
echo "[4/4] Step 4: 고급 시각화 중..."
python step4_visualization.py

if [ $? -ne 0 ]; then
    echo "❌ Step 4 실패"
    exit 1
fi

echo ""
echo "================================================================================"
echo "✅ 전체 파이프라인 완료!"
echo "================================================================================"

echo ""
echo "📁 출력 파일:"
echo "  - data/processed/*.csv (파싱 데이터)"
echo "  - data/results/학생별_상세정보.xlsx (엑셀)"
echo "  - outputs/figures/*.png (시각화)"
echo "  - data/results/hypothesis_results.csv (가설 검증)"

echo ""
echo "📊 다음 단계:"
echo "  - 엑셀 파일 확인"
echo "  - 시각화 확인"
echo "  - 가설 검증 결과 확인"
# ---------------------------------
# 3. 마무리
# ---------------------------------

# 가상 환경 비활성화
echo ""
echo "가상 환경 비활성화 중..."
deactivate
echo "✓ 비활성화 완료."

echo "========================================="
echo "모든 파이썬 스크립트가 성공적으로 실행되었습니다."
echo "========================================="

exit 0