"""
STEP 5: 보고서 생성
- 개별 학생 리포트 (텍스트 파일)
- 전체 종합 리포트 (텍스트 파일)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


def _strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼명 공백/타입 문제 방지"""
    df.columns = df.columns.astype(str).str.strip()
    return df


def load_all_data():
    """모든 데이터 로드"""
    data_dir = Path("data/processed")
    results_dir = Path("data/results")

    df_students = pd.read_csv(data_dir / "student_info.csv")
    df_grades = pd.read_csv(data_dir / "grades.csv")
    df_seteuk = pd.read_csv(data_dir / "seteuk.csv")
    df_volatility = pd.read_csv(data_dir / "volatility.csv")

    # 컬럼 정리
    df_students = _strip_columns(df_students)
    df_grades = _strip_columns(df_grades)
    df_seteuk = _strip_columns(df_seteuk)
    df_volatility = _strip_columns(df_volatility)

    # 혹시 한글 컬럼명이 섞여있을 경우 대비(있어도/없어도 안전)
    rename_map = {
        "학번": "student_id",
        "전공": "major",
        "전형": "admission_type",
        "대학입학년도": "university_admission_year",
        "입학년도": "university_admission_year",
        "고교졸업년도": "hs_graduation_year",
        "졸업년도": "hs_graduation_year",
        "코호트": "cohort",
        "COVID여부": "any_covid",
    }
    df_students = df_students.rename(columns=rename_map)

    try:
        df_hypothesis = pd.read_csv(results_dir / "hypothesis_tests.csv")
        df_hypothesis = _strip_columns(df_hypothesis)
    except:
        df_hypothesis = None

    try:
        df_summary = pd.read_csv(results_dir / "summary_statistics.csv")
        df_summary = _strip_columns(df_summary)
    except:
        df_summary = None

    return (
        df_students,
        df_grades,
        df_seteuk,
        df_volatility,
        df_hypothesis,
        df_summary,
    )


def generate_individual_report(student_id, df_students, df_grades, df_seteuk, df_volatility):
    """개별 학생 리포트 생성"""

    # 학생 정보 (없으면 빈 리포트라도 생성)
    srows = df_students[df_students["student_id"] == student_id]
    if srows.empty:
        return "\n".join([
            "=" * 80,
            "개별 학생 분석 리포트",
            "=" * 80,
            "",
            f"[오류] student_id={student_id} 학생 정보를 student_info.csv에서 찾지 못했습니다.",
            "",
            "=" * 80,
            f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
        ])
    student = srows.iloc[0]

    # 성적 데이터
    grades = df_grades[df_grades["student_id"] == student_id] if "student_id" in df_grades.columns else pd.DataFrame()

    # 세특 데이터
    seteuk = df_seteuk[df_seteuk["student_id"] == student_id] if "student_id" in df_seteuk.columns else pd.DataFrame()

    # 변동성 데이터
    volatility = df_volatility[df_volatility["student_id"] == student_id] if "student_id" in df_volatility.columns else pd.DataFrame()

    # 리포트 작성
    report = []
    report.append("=" * 80)
    report.append("개별 학생 분석 리포트")
    report.append("=" * 80)
    report.append("")

    # 학생 정보 (student_info.csv 스키마에 맞춤)
    report.append("[학생 정보]")
    report.append(f"학번: {student.get('student_id', 'N/A')}")
    report.append(f"이름: {student.get('name', 'N/A')}")
    report.append(f"전공: {student.get('major', 'N/A')}")
    report.append(f"전형: {student.get('admission_type', 'N/A')}")
    report.append(f"대학 입학년도: {student.get('university_admission_year', 'N/A')}")
    report.append(f"고교 졸업년도: {student.get('hs_graduation_year', 'N/A')}")
    report.append(f"코호트: {student.get('cohort', 'N/A')}")

    # covid_period 대신 any_covid 사용
    if "any_covid" in student.index:
        report.append(f"COVID 영향 여부(any_covid): {'COVID' if int(student.get('any_covid', 0)) == 1 else 'Pre-COVID'}")
    report.append("")

    # 성적 요약
    report.append("[성적 요약]")
    report.append(f"총 과목 수: {len(grades)}")
    if not grades.empty:
        if "grade_numeric" in grades.columns:
            report.append(f"평균 등급: {grades['grade_numeric'].mean():.2f}")
        if "achievement" in grades.columns:
            report.append(f"A 개수: {(grades['achievement'] == 'A').sum()}")
            report.append(f"B 개수: {(grades['achievement'] == 'B').sum()}")
            report.append(f"C 개수: {(grades['achievement'] == 'C').sum()}")
            report.append(f"D 개수: {(grades['achievement'] == 'D').sum()}")
        report.append("")

        if "subject_group" in grades.columns and "grade_numeric" in grades.columns:
            report.append("교과군별 평균:")
            for group in grades["subject_group"].dropna().unique():
                group_avg = grades.loc[grades["subject_group"] == group, "grade_numeric"].mean()
                report.append(f"  {group}: {group_avg:.2f}")
    report.append("")

    # 변동성
    report.append("[성적 변동성]")
    if not volatility.empty:
        vol_data = volatility.iloc[0]
        if "overall_volatility" in vol_data.index:
            report.append(f"전체 변동성: {vol_data['overall_volatility']:.3f}")
        if "overall_mean" in vol_data.index:
            report.append(f"전체 평균: {vol_data['overall_mean']:.3f}")
    report.append("")

    # 세특 요약
    report.append("[세특 요약]")
    report.append(f"총 세특 개수: {len(seteuk)}")
    if not seteuk.empty:
        if "content_length" in seteuk.columns:
            report.append(f"평균 길이: {seteuk['content_length'].mean():.0f} 자")
        if "kw_freq_exploration" in seteuk.columns:
            report.append(f"탐구/실험 키워드 빈도: {seteuk['kw_freq_exploration'].mean():.2f} (per 1000 chars)")
        if "kw_freq_online" in seteuk.columns:
            report.append(f"온라인/원격 키워드 빈도: {seteuk['kw_freq_online'].mean():.2f} (per 1000 chars)")
    report.append("")

    report.append("=" * 80)
    report.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)

    return "\n".join(report)


def generate_comprehensive_report(df_students, df_grades, df_seteuk, df_volatility,
                                  df_hypothesis, df_summary):
    """전체 종합 리포트 생성"""

    report = []
    report.append("=" * 80)
    report.append("COVID-19 대학입시 영향 분석 종합 리포트")
    report.append("=" * 80)
    report.append("")

    # 1. 연구 개요
    report.append("[1. 연구 개요]")
    report.append("본 연구는 COVID-19 팬데믹이 한국 고등학생의 내신 성적, 학생부, 그리고")
    report.append("대학 입시 전형에 미친 영향을 정량적으로 분석합니다.")
    report.append("")
    report.append("분석 대상:")
    report.append(f"  - 총 학생 수: {len(df_students)}명")

    # covid_period 대신 any_covid를 사용
    if "any_covid" in df_students.columns:
        pre_cnt = int((df_students["any_covid"] == 0).sum())
        cov_cnt = int((df_students["any_covid"] == 1).sum())
        report.append(f"  - Pre-COVID 코호트(any_covid=0): {pre_cnt}명")
        report.append(f"  - COVID 코호트(any_covid=1): {cov_cnt}명")
    elif "cohort" in df_students.columns:
        report.append("  - 코호트 분포(cohort):")
        for k, v in df_students["cohort"].value_counts(dropna=False).items():
            report.append(f"    · {k}: {int(v)}명")
    else:
        report.append("  - 코호트 구분 컬럼(any_covid/cohort)을 찾을 수 없습니다.")

    report.append(f"  - 총 성적 레코드: {len(df_grades)}건")
    report.append(f"  - 총 세특 레코드: {len(df_seteuk)}건")
    report.append("")

    # 2. 가설 검증 결과
    report.append("[2. 가설 검증 결과]")
    report.append("")

    if df_hypothesis is not None and not df_hypothesis.empty:
        for _, row in df_hypothesis.iterrows():
            hyp = row.get("hypothesis", "N/A")
            report.append(f"{hyp}:")
            if "conclusion" in row.index:
                report.append(f"  결과: {row.get('conclusion', 'N/A')}")
            if "p_value" in row.index:
                try:
                    report.append(f"  p-value: {float(row.get('p_value')):.4f}")
                except:
                    report.append(f"  p-value: {row.get('p_value')}")
            report.append("")
    else:
        report.append("  가설 검증 결과를 찾을 수 없습니다.")
        report.append("")

    # 3. 주요 발견사항
    report.append("[3. 주요 발견사항]")
    report.append("")

    if df_summary is not None and not df_summary.empty:
        report.append("코호트 간 비교:")
        for _, row in df_summary.iterrows():
            cohort = row.get("cohort", "N/A")
            report.append(f"  {cohort}:")
            if "avg_volatility" in row.index:
                report.append(f"    평균 변동성: {float(row.get('avg_volatility')):.3f}")
            if "avg_exploration_kw" in row.index:
                report.append(f"    탐구 키워드 빈도: {float(row.get('avg_exploration_kw')):.2f}")
            if "avg_online_kw" in row.index:
                report.append(f"    온라인 키워드 빈도: {float(row.get('avg_online_kw')):.2f}")
            report.append("")
    else:
        report.append("요약 통계(summary_statistics.csv)를 찾을 수 없거나 비어 있습니다.")
        report.append("")

    # 4. 결론
    report.append("[4. 결론 및 시사점]")
    report.append("")
    report.append("본 연구는 COVID-19 팬데믹이 한국 교육 시스템, 특히 고등학교 내신 평가와")
    report.append("대학 입시 과정에 상당한 영향을 미쳤음을 실증적으로 보여줍니다.")
    report.append("")
    report.append("정책적 시사점:")
    report.append("  1. 비대면 교육 환경에서의 평가 공정성 확보 방안 필요")
    report.append("  2. 학생부종합전형의 평가 기준 재검토")
    report.append("  3. 팬데믹 이후 교육 격차 해소를 위한 정책 마련")
    report.append("")

    # 5. 한계 및 후속 연구
    report.append("[5. 연구의 한계 및 후속 연구 제안]")
    report.append("")
    report.append("본 연구의 한계:")
    report.append(f"  - 제한된 표본 크기 (n={len(df_students)})")
    report.append("  - 특정 지역/학교의 데이터에 국한")
    report.append("  - 대학 실제 합격 데이터 미포함")
    report.append("")
    report.append("후속 연구 제안:")
    report.append("  - 전국 단위 대규모 데이터 분석")
    report.append("  - 대학별 실제 합격률 비교 연구")
    report.append("  - 장기적 학업 성취도 추적 연구")
    report.append("")

    report.append("=" * 80)
    report.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """메인 실행 함수"""

    print("=" * 80)
    print("STEP 5: 보고서 생성")
    print("=" * 80)

    # 데이터 로드
    print("\n데이터 로딩 중...")
    df_students, df_grades, df_seteuk, df_volatility, df_hypothesis, df_summary = load_all_data()
    print("✓ 데이터 로드 완료")

    # 출력 디렉토리
    individual_dir = Path("outputs/reports/individual")
    individual_dir.mkdir(parents=True, exist_ok=True)

    comprehensive_dir = Path("outputs/reports")
    comprehensive_dir.mkdir(parents=True, exist_ok=True)

    # 개별 리포트 생성
    print(f"\n개별 리포트 생성 중 ({len(df_students)}개)...")
    for _, student in df_students.iterrows():
        student_id = student["student_id"]

        report_content = generate_individual_report(
            student_id, df_students, df_grades, df_seteuk, df_volatility
        )

        filename = f"report_{student_id}.txt"
        with open(individual_dir / filename, "w", encoding="utf-8") as f:
            f.write(report_content)

    print(f"✓ {len(df_students)}개 개별 리포트 생성 완료")

    # 종합 리포트 생성
    print("\n종합 리포트 생성 중...")
    comprehensive_report = generate_comprehensive_report(
        df_students, df_grades, df_seteuk, df_volatility, df_hypothesis, df_summary
    )

    with open(comprehensive_dir / "comprehensive_report.txt", "w", encoding="utf-8") as f:
        f.write(comprehensive_report)

    print("✓ 종합 리포트 생성 완료")

    print("\n" + "=" * 80)
    print("보고서 생성 완료!")
    print("=" * 80)
    print(f"\n개별 리포트: {individual_dir}")
    print(f"종합 리포트: {comprehensive_dir / 'comprehensive_report.txt'}")

    print("\n" + "=" * 80)
    print("전체 분석 파이프라인 완료!")
    print("=" * 80)
    print("\n생성된 결과물:")
    print("  1. data/processed/ - 처리된 데이터 (CSV)")
    print("  2. data/results/ - 통계 분석 결과 (CSV)")
    print("  3. outputs/figures/ - 시각화 결과 (PNG)")
    print("  4. outputs/reports/ - 분석 리포트 (TXT)")


if __name__ == "__main__":
    main()
