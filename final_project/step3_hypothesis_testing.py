"""
STEP 3: 올바른 가설 검증

H1-1: 코호트 비교 (2021~2024 vs 2018~2020)
      → t-검정, 분산 비교, OLS 회귀

H1-2: 매개 분석 (세특 변화 → 변동성)
      → Mediation Analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.formula.api import ols
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """데이터 로드"""
    data_dir = Path('data/processed')

    df_students = pd.read_csv(data_dir / 'student_info.csv')
    df_grades = pd.read_csv(data_dir / 'grades.csv')
    df_seteuk = pd.read_csv(data_dir / 'seteuk.csv')
    df_volatility = pd.read_csv(data_dir / 'volatility.csv')

    return df_students, df_grades, df_seteuk, df_volatility


def hypothesis_1_1_cohort(df_students, df_volatility):
    """
    H1-1: 코호트 비교

    가설: 내신 성적의 변동성은 코로나 코호트(2021~2024)에서
          이전 코호트(2018~2020) 대비 통계적으로 유의미하게 증가

    분석 모델:
    1. t-검정 (독립표본)
    2. 분산 비교 (Levene's test, F-test)
    3. OLS 회귀 (cohort → volatility)
    """

    print("="*80)
    print("H1-1: 코호트별 성적 변동성 비교")
    print("  Pre-COVID (2018~2020) vs COVID (2021~2024)")
    print("="*80)

    # 데이터 병합
    df_merged = df_volatility.merge(
        df_students[['student_id', 'hs_graduation_year']],
        on='student_id'
    )

    # 코호트 정의
    df_merged['cohort'] = df_merged['hs_graduation_year'].apply(
        lambda x: 'Pre-COVID' if 2018 <= x <= 2020 else ('COVID' if 2021 <= x <= 2024 else 'Other')
    )

    # 분석 대상만 선택
    df_analysis = df_merged[df_merged['cohort'].isin(['Pre-COVID', 'COVID'])].copy()
    df_analysis = df_analysis.dropna(subset=['overall_volatility'])

    pre_covid = df_analysis[df_analysis['cohort'] == 'Pre-COVID']
    covid = df_analysis[df_analysis['cohort'] == 'COVID']

    print(f"\n[코호트 구성]")
    print(f"Pre-COVID (2018~2020 졸업): {len(pre_covid)}명")
    for year in range(2018, 2021):
        count = len(df_analysis[df_analysis['hs_graduation_year'] == year])
        print(f"  - {year}년: {count}명")

    print(f"\nCOVID (2021~2024 졸업): {len(covid)}명")
    for year in range(2021, 2025):
        count = len(df_analysis[df_analysis['hs_graduation_year'] == year])
        if count > 0:
            print(f"  - {year}년: {count}명")

    if len(pre_covid) < 2 or len(covid) < 2:
        print("\nWARNING: 코호트 데이터 부족 (각 코호트 최소 2명 필요)")
        return None

    # ========================================
    # 1. 기술통계
    # ========================================
    print(f"\n[1. 기술통계]")

    pre_vol = pre_covid['overall_volatility']
    covid_vol = covid['overall_volatility']

    print(f"\nPre-COVID 코호트:")
    print(f"  평균 변동성: {pre_vol.mean():.4f}")
    print(f"  표준편차: {pre_vol.std():.4f}")
    print(f"  중앙값: {pre_vol.median():.4f}")
    print(f"  범위: [{pre_vol.min():.4f}, {pre_vol.max():.4f}]")

    print(f"\nCOVID 코호트:")
    print(f"  평균 변동성: {covid_vol.mean():.4f}")
    print(f"  표준편차: {covid_vol.std():.4f}")
    print(f"  중앙값: {covid_vol.median():.4f}")
    print(f"  범위: [{covid_vol.min():.4f}, {covid_vol.max():.4f}]")

    diff_mean = covid_vol.mean() - pre_vol.mean()
    diff_pct = (diff_mean / pre_vol.mean()) * 100
    print(f"\n평균 차이: {diff_mean:+.4f} ({diff_pct:+.1f}%)")

    # ========================================
    # 2. t-검정 (독립표본)
    # ========================================
    print(f"\n[2. t-검정 (Independent Samples t-test)]")

    # Levene's test (등분산 검정)
    levene_stat, levene_p = stats.levene(pre_vol, covid_vol)
    print(f"\nLevene's test (등분산 검정):")
    print(f"  통계량: {levene_stat:.4f}")
    print(f"  p-value: {levene_p:.4f}")

    if levene_p > 0.05:
        print(f"  -> 등분산 가정 만족 (p > 0.05)")
        # Student's t-test
        t_stat, p_value = stats.ttest_ind(covid_vol, pre_vol, equal_var=True)
        test_name = "Student's t-test"
    else:
        print(f"  -> 등분산 가정 위배 (p < 0.05)")
        # Welch's t-test
        t_stat, p_value = stats.ttest_ind(covid_vol, pre_vol, equal_var=False)
        test_name = "Welch's t-test"

    print(f"\n{test_name}:")
    print(f"  t-통계량: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}")
    print(f"  자유도: {len(covid_vol) + len(pre_vol) - 2}")

    if p_value < 0.001:
        sig_level = "p < 0.001 ***"
    elif p_value < 0.01:
        sig_level = "p < 0.01 **"
    elif p_value < 0.05:
        sig_level = "p < 0.05 *"
    else:
        sig_level = "p >= 0.05 (n.s.)"

    print(f"  유의수준: {sig_level}")

    if p_value < 0.05:
        direction = "높음" if covid_vol.mean() > pre_vol.mean() else "낮음"
        print(f"  CONCLUSION: COVID 코호트의 변동성이 유의미하게 {direction}")
    else:
        print(f"  CONCLUSION: 두 코호트 간 유의미한 차이 없음")

    # Effect size (Cohen's d)
    pooled_std = np.sqrt(
        ((len(pre_vol)-1)*pre_vol.std()**2 + (len(covid_vol)-1)*covid_vol.std()**2) /
        (len(pre_vol)+len(covid_vol)-2)
    )
    cohens_d = (covid_vol.mean() - pre_vol.mean()) / pooled_std

    print(f"\nEffect Size (Cohen's d): {cohens_d:.4f}")
    if abs(cohens_d) < 0.2:
        effect_interpretation = "작음 (small)"
    elif abs(cohens_d) < 0.5:
        effect_interpretation = "중간 (medium)"
    elif abs(cohens_d) < 0.8:
        effect_interpretation = "큼 (large)"
    else:
        effect_interpretation = "매우 큼 (very large)"
    print(f"  해석: {effect_interpretation}")

    # ========================================
    # 3. 분산 비교
    # ========================================
    print(f"\n[3. 분산 비교]")

    var_pre = pre_vol.var()
    var_covid = covid_vol.var()

    print(f"\nPre-COVID 분산: {var_pre:.4f}")
    print(f"COVID 분산: {var_covid:.4f}")
    print(f"분산 비율 (COVID/Pre): {var_covid/var_pre:.4f}")

    # F-test for variance
    f_stat = var_covid / var_pre if var_covid > var_pre else var_pre / var_covid
    df1 = len(covid_vol) - 1 if var_covid > var_pre else len(pre_vol) - 1
    df2 = len(pre_vol) - 1 if var_covid > var_pre else len(covid_vol) - 1
    f_p = 1 - stats.f.cdf(f_stat, df1, df2)

    print(f"\nF-test (분산의 동질성):")
    print(f"  F-통계량: {f_stat:.4f}")
    print(f"  p-value: {f_p:.4f}")

    if f_p < 0.05:
        print(f"  RESULT: 두 코호트의 분산이 유의미하게 다름")
    else:
        print(f"  RESULT: 두 코호트의 분산 차이 없음")

    # ========================================
    # 4. OLS 회귀 분석
    # ========================================
    print(f"\n[4. OLS 회귀 분석]")

    # 코호트를 더미 변수로
    df_analysis['is_covid'] = (df_analysis['cohort'] == 'COVID').astype(int)

    print(f"\n회귀 모델: volatility ~ is_covid")
    print(f"  (is_covid: 0=Pre-COVID, 1=COVID)")

    try:
        model = ols('overall_volatility ~ is_covid', data=df_analysis).fit()

        print(f"\n회귀 결과:")
        print(f"  R^2: {model.rsquared:.4f}")
        print(f"  Adj. R^2: {model.rsquared_adj:.4f}")
        print(f"  F-통계량: {model.fvalue:.4f}")
        print(f"  F p-value: {model.f_pvalue:.4f}")

        print(f"\n계수 추정:")
        print(f"  절편 (Pre-COVID 평균): {model.params['Intercept']:.4f}")
        print(f"    p-value: {model.pvalues['Intercept']:.4f}")

        print(f"  is_covid (COVID 효과): {model.params['is_covid']:.4f}")
        print(f"    p-value: {model.pvalues['is_covid']:.4f}")
        print(f"    95% CI: [{model.conf_int().loc['is_covid', 0]:.4f}, {model.conf_int().loc['is_covid', 1]:.4f}]")

        if model.pvalues['is_covid'] < 0.05:
            direction = "증가" if model.params['is_covid'] > 0 else "감소"
            print(f"  RESULT: COVID 코호트에서 변동성이 유의미하게 {direction}")
        else:
            print(f"  RESULT: COVID 효과 유의미하지 않음")

        # 잔차 진단
        print(f"\n잔차 진단:")
        residuals = model.resid
        _, shapiro_p = stats.shapiro(residuals)
        print(f"  Shapiro-Wilk (정규성): p={shapiro_p:.4f}")
        if shapiro_p > 0.05:
            print(f"    -> 정규성 가정 만족")
        else:
            print(f"    -> 정규성 가정 위배 (주의)")

    except Exception as e:
        print(f"  ERROR: 회귀 분석 실패: {e}")

    # ========================================
    # 요약
    # ========================================
    print(f"\n" + "="*80)
    print(f"H1-1 검증 결과 요약")
    print(f"="*80)

    print(f"\n가설: COVID 코호트의 변동성이 Pre-COVID보다 높다")
    print(f"\n결과:")
    print(f"  1. t-검정: t={t_stat:.4f}, {sig_level}")
    print(f"  2. 효과 크기: Cohen's d={cohens_d:.4f} ({effect_interpretation})")
    print(f"  3. 평균 차이: {diff_mean:+.4f} ({diff_pct:+.1f}%)")

    if p_value < 0.05 and diff_mean > 0:
        print(f"\nRESULT: 가설 채택 (COVID 코호트 변동성 유의미 증가)")
    elif p_value < 0.05 and diff_mean < 0:
        print(f"\nRESULT: 가설 기각 (COVID 코호트 변동성 감소)")
    else:
        print(f"\nRESULT: 가설 기각 (유의미한 차이 없음)")

    return {
        'hypothesis': 'H1-1',
        'pre_covid_n': len(pre_vol),
        'covid_n': len(covid_vol),
        'pre_covid_mean': pre_vol.mean(),
        'covid_mean': covid_vol.mean(),
        'difference': diff_mean,
        'difference_pct': diff_pct,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'significant': p_value < 0.05,
        'hypothesis_supported': p_value < 0.05 and diff_mean > 0
    }


def hypothesis_1_2_mediation(df_students, df_seteuk, df_volatility):
    """
    H1-2: 매개 분석
    """

    print("\n" + "="*80)
    print("H1-2: 매개 분석 (Mediation Analysis)")
    print("  경로: Cohort -> 세특 키워드 변화 -> 변동성")
    print("="*80)

    # 학생별 세특 키워드 평균
    seteuk_summary = df_seteuk.groupby('student_id').agg({
        'kw_freq_exploration': 'mean',
        'kw_freq_online': 'mean',
        'kw_freq_qualitative': 'mean'
    }).reset_index()

    # 병합
    df_merged = df_volatility.merge(
        df_students[['student_id', 'hs_graduation_year']],
        on='student_id'
    ).merge(seteuk_summary, on='student_id', how='left')

    # 코호트 정의
    df_merged['cohort'] = df_merged['hs_graduation_year'].apply(
        lambda x: 'Pre-COVID' if 2018 <= x <= 2020 else ('COVID' if 2021 <= x <= 2024 else 'Other')
    )
    df_merged['is_covid'] = (df_merged['cohort'] == 'COVID').astype(int)

    # 분석 대상
    df_analysis = df_merged[
        df_merged['cohort'].isin(['Pre-COVID', 'COVID'])
    ].dropna(subset=['overall_volatility', 'kw_freq_exploration', 'kw_freq_online'])

    print(f"\n[분석 대상]")
    print(f"전체: {len(df_analysis)}명")
    print(f"  Pre-COVID: {(df_analysis['cohort']=='Pre-COVID').sum()}명")
    print(f"  COVID: {(df_analysis['cohort']=='COVID').sum()}명")

    if len(df_analysis) < 10:
        print("\nWARNING: 데이터 부족 (최소 10명 필요)")
        return None

    # ========================================
    # 1. 경로 분석
    # ========================================
    print(f"\n[1. 경로별 분석]")

    print(f"\n경로 a: Cohort -> 탐구 키워드")
    model_a1 = ols('kw_freq_exploration ~ is_covid', data=df_analysis).fit()
    print(f"  계수: {model_a1.params['is_covid']:.4f}")
    print(f"  p-value: {model_a1.pvalues['is_covid']:.4f}")
    if model_a1.pvalues['is_covid'] < 0.05:
        direction = "감소" if model_a1.params['is_covid'] < 0 else "증가"
        print(f"  RESULT: COVID 코호트에서 탐구 키워드 {direction}")

    print(f"\n경로 a': Cohort -> 온라인 키워드")
    model_a2 = ols('kw_freq_online ~ is_covid', data=df_analysis).fit()
    print(f"  계수: {model_a2.params['is_covid']:.4f}")
    print(f"  p-value: {model_a2.pvalues['is_covid']:.4f}")
    if model_a2.pvalues['is_covid'] < 0.05:
        direction = "증가" if model_a2.params['is_covid'] > 0 else "감소"
        print(f"  RESULT: COVID 코호트에서 온라인 키워드 {direction}")

    print(f"\n경로 b: 키워드 -> 변동성 (매개변수 통제)")
    model_b = ols('overall_volatility ~ kw_freq_exploration + kw_freq_online',
                  data=df_analysis).fit()
    print(f"  탐구 키워드 계수: {model_b.params['kw_freq_exploration']:.4f}")
    print(f"    p-value: {model_b.pvalues['kw_freq_exploration']:.4f}")
    print(f"  온라인 키워드 계수: {model_b.params['kw_freq_online']:.4f}")
    print(f"    p-value: {model_b.pvalues['kw_freq_online']:.4f}")

    print(f"\n경로 c: Cohort -> 변동성 (총 효과)")
    model_c = ols('overall_volatility ~ is_covid', data=df_analysis).fit()
    total_effect = model_c.params['is_covid']
    print(f"  총 효과: {total_effect:.4f}")
    print(f"  p-value: {model_c.pvalues['is_covid']:.4f}")

    print(f"\n경로 c': Cohort -> 변동성 (직접 효과)")
    model_c_prime = ols('overall_volatility ~ is_covid + kw_freq_exploration + kw_freq_online',
                        data=df_analysis).fit()
    direct_effect = model_c_prime.params['is_covid']
    print(f"  직접 효과: {direct_effect:.4f}")
    print(f"  p-value: {model_c_prime.pvalues['is_covid']:.4f}")

    # ========================================
    # 2. 매개 효과 계산
    # ========================================
    print(f"\n[2. 매개 효과]")

    mediation_exploration = model_a1.params['is_covid'] * model_b.params['kw_freq_exploration']
    print(f"\n탐구 키워드 매개 효과:")
    print(f"  a x b = {model_a1.params['is_covid']:.4f} x {model_b.params['kw_freq_exploration']:.4f}")
    print(f"  = {mediation_exploration:.4f}")

    mediation_online = model_a2.params['is_covid'] * model_b.params['kw_freq_online']
    print(f"\n온라인 키워드 매개 효과:")
    print(f"  a x b = {model_a2.params['is_covid']:.4f} x {model_b.params['kw_freq_online']:.4f}")
    print(f"  = {mediation_online:.4f}")

    total_mediation = mediation_exploration + mediation_online
    print(f"\n총 매개 효과: {total_mediation:.4f}")

    if abs(total_effect) > 0.0001:
        mediation_ratio = (total_mediation / total_effect) * 100
        print(f"매개 효과 비율: {mediation_ratio:.1f}%")
        print(f"  (총 효과 중 매개변수를 통한 효과의 비율)")
    else:
        mediation_ratio = 0

    # ========================================
    # 3. Sobel Test
    # ========================================
    print(f"\n[3. Sobel Test (매개 효과 유의성)]")

    a1 = model_a1.params['is_covid']
    b1 = model_b.params['kw_freq_exploration']
    se_a1 = model_a1.bse['is_covid']
    se_b1 = model_b.bse['kw_freq_exploration']

    sobel_se_1 = np.sqrt(b1**2 * se_a1**2 + a1**2 * se_b1**2)
    sobel_z_1 = mediation_exploration / sobel_se_1
    sobel_p_1 = 2 * (1 - stats.norm.cdf(abs(sobel_z_1)))

    print(f"\n탐구 키워드 매개:")
    print(f"  Sobel Z: {sobel_z_1:.4f}")
    print(f"  p-value: {sobel_p_1:.4f}")
    if sobel_p_1 < 0.05:
        print(f"  RESULT: 매개 효과 유의미함")

    a2 = model_a2.params['is_covid']
    b2 = model_b.params['kw_freq_online']
    se_a2 = model_a2.bse['is_covid']
    se_b2 = model_b.bse['kw_freq_online']

    sobel_se_2 = np.sqrt(b2**2 * se_a2**2 + a2**2 * se_b2**2)
    sobel_z_2 = mediation_online / sobel_se_2
    sobel_p_2 = 2 * (1 - stats.norm.cdf(abs(sobel_z_2)))

    print(f"\n온라인 키워드 매개:")
    print(f"  Sobel Z: {sobel_z_2:.4f}")
    print(f"  p-value: {sobel_p_2:.4f}")
    if sobel_p_2 < 0.05:
        print(f"  RESULT: 매개 효과 유의미함")

    # ========================================
    # 요약
    # ========================================
    print(f"\n" + "="*80)
    print(f"H1-2 검증 결과 요약")
    print(f"="*80)

    print(f"\n가설: 세특 키워드 변화가 변동성 증가를 매개")
    print(f"\n경로:")
    print(f"  1. Cohort -> 탐구: {model_a1.params['is_covid']:.4f} (p={model_a1.pvalues['is_covid']:.4f})")
    print(f"  2. Cohort -> 온라인: {model_a2.params['is_covid']:.4f} (p={model_a2.pvalues['is_covid']:.4f})")
    print(f"  3. 탐구 -> 변동성: {model_b.params['kw_freq_exploration']:.4f} (p={model_b.pvalues['kw_freq_exploration']:.4f})")
    print(f"  4. 온라인 -> 변동성: {model_b.params['kw_freq_online']:.4f} (p={model_b.pvalues['kw_freq_online']:.4f})")

    print(f"\n효과:")
    print(f"  총 효과 (c): {total_effect:.4f}")
    print(f"  직접 효과 (c'): {direct_effect:.4f}")
    print(f"  매개 효과 (a x b): {total_mediation:.4f}")

    if abs(total_effect) > 0.0001:
        print(f"  매개 비율: {mediation_ratio:.1f}%")

    mediation_significant = (sobel_p_1 < 0.05 or sobel_p_2 < 0.05)

    if mediation_significant and abs(total_mediation) > 0.01:
        if abs(direct_effect) < 0.01:
            print(f"\nRESULT: 완전 매개 (Full Mediation)")
        else:
            print(f"\nRESULT: 부분 매개 (Partial Mediation)")
    else:
        print(f"\nRESULT: 매개 효과 없음")

    return {
        'hypothesis': 'H1-2',
        'n': len(df_analysis),
        'total_effect': total_effect,
        'direct_effect': direct_effect,
        'mediation_effect': total_mediation,
        'mediation_ratio': mediation_ratio if abs(total_effect) > 0.0001 else 0,
        'sobel_p_exploration': sobel_p_1,
        'sobel_p_online': sobel_p_2,
        'mediation_significant': mediation_significant
    }


def main():
    """메인 함수"""

    print("\n" + "="*80)
    print("STEP 3: 올바른 가설 검증")
    print("  H1-1: 코호트 비교 (t-검정, 분산, OLS)")
    print("  H1-2: 매개 분석 (Mediation)")
    print("="*80)

    # 데이터 로드
    print("\n데이터 로딩 중...")
    try:
        df_students, df_grades, df_seteuk, df_volatility = load_data()
        print(f"OK: 학생: {len(df_students)}명")
        print(f"OK: 성적: {len(df_grades)}건")
        print(f"OK: 세특: {len(df_seteuk)}건")
        print(f"OK: 변동성: {len(df_volatility)}건")
    except Exception as e:
        print(f"ERROR: 데이터 로드 실패: {e}")
        print("\n먼저 step1_final_complete.py를 실행하세요!")
        return

    results_h1_1 = hypothesis_1_1_cohort(df_students, df_volatility)
    results_h1_2 = hypothesis_1_2_mediation(df_students, df_seteuk, df_volatility)

    results_dir = Path('data/results')
    results_dir.mkdir(parents=True, exist_ok=True)

    results = []
    if results_h1_1:
        results.append(results_h1_1)
    if results_h1_2:
        results.append(results_h1_2)

    if results:
        df_results = pd.DataFrame(results)
        df_results.to_csv(results_dir / 'hypothesis_results.csv', index=False, encoding='utf-8-sig')
        print(f"\nRESULT SAVED: data/results/hypothesis_results.csv")

    print("\n" + "="*80)
    print("가설 검증 완료")
    print("="*80)

if __name__ == "__main__":
    main()
