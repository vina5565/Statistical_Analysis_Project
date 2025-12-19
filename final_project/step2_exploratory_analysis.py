"""
STEP 2: 탐색적 데이터 분석 (EDA)
- 새 데이터 구조 완벽 호환
- 학년별 코로나 분석
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False


def load_data():
    """데이터 로드"""
    data_dir = Path('data/processed')

    df_students = pd.read_csv(data_dir / 'student_info.csv')
    df_grades = pd.read_csv(data_dir / 'grades.csv')
    df_seteuk = pd.read_csv(data_dir / 'seteuk.csv')
    df_volatility = pd.read_csv(data_dir / 'volatility.csv')

    return df_students, df_grades, df_seteuk, df_volatility


def descriptive_statistics(df_students, df_grades, df_seteuk, df_volatility):
    """기술통계"""

    print("=" * 80)
    print("1. 기술통계량")
    print("=" * 80)

    # 학생 정보
    print("\n[학생 정보]")
    print(f"총 학생 수: {len(df_students)}")

    if 'is_repeat' in df_students.columns:
        print("\n재수 여부:")
        print(f"  현역: {(df_students['is_repeat'] == 0).sum()}명")
        print(f"  재수생: {(df_students['is_repeat'] == 1).sum()}명")

    if 'any_covid' in df_students.columns:
        print("\n코로나 경험 (원격수업 기반):")
        print(f"  있음: {(df_students['any_covid'] == 1).sum()}명")
        print(f"  없음: {(df_students['any_covid'] == 0).sum()}명")

    # 학년별 코로나
    print("\n학년별 코로나 경험:")
    for grade in [1, 2, 3]:
        col = f'grade{grade}_covid'
        if col in df_students.columns:
            count = (df_students[col] == 1).sum()
            print(f"  {grade}학년: {count}명")

    # 졸업년도
    if 'hs_graduation_year' in df_students.columns:
        print("\n고교 졸업년도 분포:")
        year_dist = df_students['hs_graduation_year'].value_counts().sort_index()
        for year, count in year_dist.items():
            print(f"  {year}년: {count}명")

    # 전공
    if 'major' in df_students.columns:
        print("\n전공 분포:")
        major_dist = df_students['major'].value_counts()
        for major, count in major_dist.head(10).items():
            print(f"  {major}: {count}명")

    # 성적 정보
    print("\n[성적 정보]")
    print(f"총 성적 레코드: {len(df_grades)}건")

    if 'grade_type' in df_grades.columns:
        print("\n평가 방식:")
        for gtype in df_grades['grade_type'].unique():
            count = (df_grades['grade_type'] == gtype).sum()
            type_name = '절대평가' if gtype == 'achievement' else '상대평가'
            print(f"  {type_name}: {count}건")

    if 'subject_group' in df_grades.columns:
        print("\n교과군별 과목 수:")
        group_dist = df_grades['subject_group'].value_counts()
        for group, count in group_dist.head(10).items():
            print(f"  {group}: {count}건")

    # 학년별 성적 분포
    if 'grade_year' in df_grades.columns:
        print("\n학년별 성적 건수:")
        for grade in [1, 2, 3]:
            count = (df_grades['grade_year'] == grade).sum()
            print(f"  {grade}학년: {count}건")

    # 세특 정보
    print("\n[세특 정보]")
    print(f"총 세특 레코드: {len(df_seteuk)}건")

    if 'content_length' in df_seteuk.columns:
        print(f"평균 세특 길이: {df_seteuk['content_length'].mean():.1f}자")
        print(f"최소/최대 길이: {df_seteuk['content_length'].min()}자 / {df_seteuk['content_length'].max()}자")

    # 키워드 빈도
    if 'kw_freq_exploration' in df_seteuk.columns:
        print("\n키워드 빈도 (per 1000자):")
        print(f"  탐구: {df_seteuk['kw_freq_exploration'].mean():.2f}")
        print(f"  온라인: {df_seteuk['kw_freq_online'].mean():.2f}")
        print(f"  정성평가: {df_seteuk['kw_freq_qualitative'].mean():.2f}")

    # 변동성 정보
    print("\n[변동성 정보]")

    if 'overall_volatility' in df_volatility.columns:
        valid = df_volatility['overall_volatility'].dropna()
        if len(valid) > 0:
            print(f"전체 평균 변동성: {valid.mean():.3f} ± {valid.std():.3f}")
            print(f"최소/최대: {valid.min():.3f} / {valid.max():.3f}")

    # 학년별 변동성
    print("\n학년별 평균 변동성:")
    for grade in [1, 2, 3]:
        col = f'grade{grade}_volatility'
        if col in df_volatility.columns:
            valid = df_volatility[col].dropna()
            if len(valid) > 0:
                print(f"  {grade}학년: {valid.mean():.3f} ± {valid.std():.3f}")


def covid_comparison(df_students, df_grades, df_volatility):
    """코로나 그룹 비교"""

    print("\n" + "=" * 80)
    print("2. 코로나 그룹 비교 (원격수업 기반)")
    print("=" * 80)

    if 'any_covid' not in df_students.columns:
        print("코로나 정보 없음")
        return

    # 전체 비교
    no_covid = df_students[df_students['any_covid'] == 0]
    has_covid = df_students[df_students['any_covid'] == 1]

    print("\n[전체 비교]")
    print(f"코로나 없음: {len(no_covid)}명")
    print(f"코로나 있음: {len(has_covid)}명")

    # 변동성 비교
    if 'overall_volatility' in df_volatility.columns:
        vol_no_covid = df_volatility[
            df_volatility['student_id'].isin(no_covid['student_id'])
        ]['overall_volatility'].dropna()

        vol_has_covid = df_volatility[
            df_volatility['student_id'].isin(has_covid['student_id'])
        ]['overall_volatility'].dropna()

        if len(vol_no_covid) > 0 and len(vol_has_covid) > 0:
            print("\n전체 변동성:")
            print(f"  코로나 없음: {vol_no_covid.mean():.3f} ± {vol_no_covid.std():.3f}")
            print(f"  코로나 있음: {vol_has_covid.mean():.3f} ± {vol_has_covid.std():.3f}")
            print(f"  차이: {vol_has_covid.mean() - vol_no_covid.mean():+.3f}")

    # 학년별 비교
    print("\n[학년별 원격수업 경험자]")
    for grade in [1, 2, 3]:
        col = f'grade{grade}_covid'
        if col in df_students.columns:
            count = (df_students[col] == 1).sum()
            pct = count / len(df_students) * 100
            print(f"  {grade}학년: {count}명 ({pct:.1f}%)")

            vol_col = f'grade{grade}_volatility'
            if vol_col in df_volatility.columns:
                no_remote_ids = df_students[df_students[col] == 0]['student_id']
                vol_no = df_volatility[
                    df_volatility['student_id'].isin(no_remote_ids)
                ][vol_col].dropna()

                has_remote_ids = df_students[df_students[col] == 1]['student_id']
                vol_yes = df_volatility[
                    df_volatility['student_id'].isin(has_remote_ids)
                ][vol_col].dropna()

                if len(vol_no) > 0 and len(vol_yes) > 0:
                    print(f"    원격 없음: {vol_no.mean():.3f}")
                    print(f"    원격 있음: {vol_yes.mean():.3f}")


def grade_distribution(df_grades):
    """등급 분포 (유효한 등급만 집계, 그 외 무시)"""

    print("\n" + "=" * 80)
    print("3. 등급 분포")
    print("=" * 80)

    if 'grade_type' not in df_grades.columns or 'achievement' not in df_grades.columns:
        print("등급 정보 없음")
        return

    # 공통 전처리: 공백 제거 + 결측 제거
    tmp = df_grades.copy()
    tmp['achievement'] = tmp['achievement'].astype(str).str.strip()
    tmp = tmp[tmp['achievement'].notna() & (tmp['achievement'] != '') & (tmp['achievement'].str.lower() != 'nan')]

    # 1) 절대평가: A~E만 인정
    ach_valid_set = set(list("ABCDE"))
    ach = tmp[tmp['grade_type'] == 'achievement'].copy()
    ach = ach[ach['achievement'].isin(ach_valid_set)]

    if len(ach) > 0:
        print("\n[절대평가 (A~E) - 유효값만]")
        dist = ach['achievement'].value_counts().reindex(list("ABCDE")).dropna()
        denom = dist.sum()  # 유효한 값만 기준으로 퍼센트
        for g, c in dist.items():
            pct = c / denom * 100
            print(f"  {g}: {c}건 ({pct:.1f}%)")

    # 2) 상대평가: 1~9만 인정 (정수/문자 모두 처리)
    rank = tmp[tmp['grade_type'] == 'rank'].copy()

    # 숫자 형태만 남기고 int로 변환 시도 -> 실패는 NaN으로
    rank['rank_num'] = pd.to_numeric(rank['achievement'], errors='coerce')

    # 1~9 정수만 인정 (1.0 같은 것도 허용하되 정수 조건 체크)
    rank = rank[rank['rank_num'].between(1, 9)]
    rank = rank[rank['rank_num'] % 1 == 0]  # 정수만
    rank['rank_num'] = rank['rank_num'].astype(int)

    if len(rank) > 0:
        print("\n[상대평가 (1~9) - 유효값만]")
        dist = rank['rank_num'].value_counts().reindex(range(1, 10)).dropna()
        denom = dist.sum()  # 유효한 값만 기준으로 퍼센트
        for g, c in dist.items():
            pct = c / denom * 100
            print(f"  {g}: {c}건 ({pct:.1f}%)")



def create_visualizations(df_students, df_grades, df_volatility):
    """시각화"""

    print("\n" + "=" * 80)
    print("4. 시각화 생성")
    print("=" * 80)

    output_dir = Path('outputs/figures')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 졸업년도 분포
    if 'hs_graduation_year' in df_students.columns:
        plt.figure(figsize=(10, 6))
        year_counts = df_students['hs_graduation_year'].value_counts().sort_index()
        plt.bar(year_counts.index, year_counts.values, color='steelblue', alpha=0.7)
        plt.xlabel('Graduation Year', fontsize=12)
        plt.ylabel('Number of Students', fontsize=12)
        plt.title('Distribution of High School Graduation Years', fontsize=14, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'graduation_year_dist.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  graduation_year_dist.png")

    # 2. 코로나 경험
    if 'any_covid' in df_students.columns:
        plt.figure(figsize=(8, 6))
        covid_counts = df_students['any_covid'].value_counts()
        labels = ['No COVID', 'Has COVID']
        colors = ['lightcoral', 'lightblue']
        plt.pie(covid_counts.values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('COVID-19 Exposure (Remote Learning)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_dir / 'covid_exposure.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  covid_exposure.png")

    # 3. 학년별 코로나
    grade_covid_data = []
    for grade in [1, 2, 3]:
        col = f'grade{grade}_covid'
        if col in df_students.columns:
            count = (df_students[col] == 1).sum()
            grade_covid_data.append({'Grade': f'Grade {grade}', 'Count': count})

    if grade_covid_data:
        df_plot = pd.DataFrame(grade_covid_data)
        plt.figure(figsize=(8, 6))
        plt.bar(df_plot['Grade'], df_plot['Count'], color='coral', alpha=0.7)
        plt.xlabel('Grade Level', fontsize=12)
        plt.ylabel('Number of Students', fontsize=12)
        plt.title('Students with Remote Learning by Grade', fontsize=14, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'covid_by_grade.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  covid_by_grade.png")

    # 4. 변동성 분포
    if 'overall_volatility' in df_volatility.columns:
        valid_vol = df_volatility['overall_volatility'].dropna()
        if len(valid_vol) > 0:
            plt.figure(figsize=(10, 6))
            plt.hist(valid_vol, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
            plt.xlabel('Volatility', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.title('Distribution of Grade Volatility', fontsize=14, fontweight='bold')
            plt.axvline(valid_vol.mean(), color='red', linestyle='--', label=f'Mean: {valid_vol.mean():.3f}')
            plt.legend()
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir / 'volatility_dist.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  volatility_dist.png")

    # 5. 코로나별 변동성 비교
    if 'any_covid' in df_students.columns and 'overall_volatility' in df_volatility.columns:
        merged = df_volatility.merge(df_students[['student_id', 'any_covid']], on='student_id')
        valid = merged.dropna(subset=['overall_volatility'])

        if len(valid) > 0:
            plt.figure(figsize=(10, 6))

            no_covid_vol = valid[valid['any_covid'] == 0]['overall_volatility']
            has_covid_vol = valid[valid['any_covid'] == 1]['overall_volatility']

            plt.boxplot([no_covid_vol, has_covid_vol], labels=['No COVID', 'Has COVID'])
            plt.ylabel('Volatility', fontsize=12)
            plt.title('Grade Volatility by COVID-19 Exposure', fontsize=14, fontweight='bold')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir / 'volatility_by_covid.png', dpi=300, bbox_inches='tight')
            plt.close()
            print("  volatility_by_covid.png")

    print(f"\n모든 시각화 저장: {output_dir}")


def main():
    """메인 함수"""

    print("\n" + "=" * 80)
    print("STEP 2: 탐색적 데이터 분석 (EDA)")
    print("=" * 80)

    print("\n데이터 로딩 중...")
    try:
        df_students, df_grades, df_seteuk, df_volatility = load_data()
        print("데이터 로드 완료")
    except Exception as e:
        print(f"데이터 로드 실패: {e}")
        print("\n먼저 step1_final_complete.py를 실행하세요.")
        return

    descriptive_statistics(df_students, df_grades, df_seteuk, df_volatility)
    covid_comparison(df_students, df_grades, df_volatility)
    grade_distribution(df_grades)
    create_visualizations(df_students, df_grades, df_volatility)

    print("\n" + "=" * 80)
    print("EDA 완료")
    print("=" * 80)
    print("\n출력 파일:")
    print("  - outputs/figures/*.png (시각화)")


if __name__ == "__main__":
    main()
