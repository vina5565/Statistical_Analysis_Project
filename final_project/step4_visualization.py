"""
STEP 4: 시각화 생성
- 새 데이터 구조 완전 호환
- 학년별 코로나 시각화
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


def create_h1_1_figures(df_students, df_grades, df_volatility, output_dir):
    """H1-1: 원격수업과 성적 변동성 시각화"""
    
    print("\n[H1-1 시각화]")
    
    # 학년별 데이터 구성
    grade_level_data = []
    
    for _, student in df_students.iterrows():
        student_id = student['student_id']
        
        for grade in [1, 2, 3]:
            # 해당 학년 성적
            grade_data = df_grades[
                (df_grades['student_id'] == student_id) & 
                (df_grades['grade_year'] == grade)
            ]
            
            if len(grade_data) == 0:
                continue
            
            # 절대평가만
            ach_data = grade_data[grade_data['grade_type'] == 'achievement']
            
            if len(ach_data) > 1:
                volatility = ach_data['grade_numeric'].std()
                mean_grade = ach_data['grade_numeric'].mean()
                
                # 코로나 여부
                has_remote = student[f'grade{grade}_covid'] == 1
                
                grade_level_data.append({
                    'student_id': student_id,
                    'grade': grade,
                    'has_remote': 1 if has_remote else 0,
                    'volatility': volatility,
                    'mean_grade': mean_grade
                })
    
    df_analysis = pd.DataFrame(grade_level_data)
    
    if len(df_analysis) == 0:
        print("  ⚠️  데이터 부족")
        return
    
    # 1. Boxplot: 원격수업 여부별 변동성
    fig, ax = plt.subplots(figsize=(10, 6))
    
    no_remote = df_analysis[df_analysis['has_remote'] == 0]['volatility']
    has_remote = df_analysis[df_analysis['has_remote'] == 1]['volatility']
    
    bp = ax.boxplot([no_remote, has_remote], 
                     labels=['No Remote\nLearning', 'Has Remote\nLearning'],
                     patch_artist=True)
    
    # 색상
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    
    ax.set_ylabel('Grade Volatility (SD)', fontsize=12)
    ax.set_title('Grade Volatility by Remote Learning Status\n(Grade-Level Analysis)', 
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # 통계 정보
    textstr = f'No Remote: {no_remote.mean():.3f} ± {no_remote.std():.3f} (n={len(no_remote)})\n'
    textstr += f'Has Remote: {has_remote.mean():.3f} ± {has_remote.std():.3f} (n={len(has_remote)})'
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'h1_1_volatility_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ h1_1_volatility_boxplot.png")
    
    # 2. Violin plot: 학년별 비교
    fig, ax = plt.subplots(figsize=(12, 6))
    
    plot_data = []
    for grade in [1, 2, 3]:
        grade_data = df_analysis[df_analysis['grade'] == grade]
        for _, row in grade_data.iterrows():
            plot_data.append({
                'Grade': f'Grade {grade}',
                'Remote': 'Has Remote' if row['has_remote'] == 1 else 'No Remote',
                'Volatility': row['volatility']
            })
    
    df_plot = pd.DataFrame(plot_data)
    
    if len(df_plot) > 0:
        sns.violinplot(data=df_plot, x='Grade', y='Volatility', hue='Remote', 
                      palette={'No Remote': 'lightblue', 'Has Remote': 'lightcoral'},
                      split=False, ax=ax)
        
        ax.set_ylabel('Grade Volatility (SD)', fontsize=12)
        ax.set_xlabel('Grade Level', fontsize=12)
        ax.set_title('Grade Volatility by Grade Level and Remote Learning', 
                     fontsize=14, fontweight='bold')
        ax.legend(title='Remote Learning', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'h1_1_volatility_violin.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ h1_1_volatility_violin.png")
    
    # 3. Bar plot: 학년별 평균 비교
    fig, ax = plt.subplots(figsize=(12, 6))
    
    grade_summary = []
    for grade in [1, 2, 3]:
        grade_data = df_analysis[df_analysis['grade'] == grade]
        
        no_remote_g = grade_data[grade_data['has_remote'] == 0]['volatility']
        has_remote_g = grade_data[grade_data['has_remote'] == 1]['volatility']
        
        if len(no_remote_g) > 0:
            grade_summary.append({
                'Grade': f'Grade {grade}',
                'Type': 'No Remote',
                'Mean': no_remote_g.mean(),
                'SE': no_remote_g.std() / np.sqrt(len(no_remote_g))
            })
        
        if len(has_remote_g) > 0:
            grade_summary.append({
                'Grade': f'Grade {grade}',
                'Type': 'Has Remote',
                'Mean': has_remote_g.mean(),
                'SE': has_remote_g.std() / np.sqrt(len(has_remote_g))
            })
    
    df_summary = pd.DataFrame(grade_summary)
    
    if len(df_summary) > 0:
        x = np.arange(3)
        width = 0.35
        
        no_remote_data = df_summary[df_summary['Type'] == 'No Remote']
        has_remote_data = df_summary[df_summary['Type'] == 'Has Remote']
        
        ax.bar(x - width/2, no_remote_data['Mean'], width, 
               yerr=no_remote_data['SE'], label='No Remote',
               color='lightblue', capsize=5)
        ax.bar(x + width/2, has_remote_data['Mean'], width,
               yerr=has_remote_data['SE'], label='Has Remote',
               color='lightcoral', capsize=5)
        
        ax.set_ylabel('Mean Volatility (SD)', fontsize=12)
        ax.set_xlabel('Grade Level', fontsize=12)
        ax.set_title('Mean Grade Volatility by Grade Level and Remote Learning',
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['Grade 1', 'Grade 2', 'Grade 3'])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'h1_1_volatility_by_grade.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ h1_1_volatility_by_grade.png")


def create_h1_2_figures(df_students, df_seteuk, output_dir):
    """H1-2: 원격수업과 세특 키워드 시각화"""
    
    print("\n[H1-2 시각화]")
    
    # 학년별 세특 + 코로나
    seteuk_analysis = []
    
    for _, student in df_students.iterrows():
        student_id = student['student_id']
        
        for grade in [1, 2, 3]:
            grade_seteuk = df_seteuk[
                (df_seteuk['student_id'] == student_id) & 
                (df_seteuk['grade_year'] == grade)
            ]
            
            if len(grade_seteuk) == 0:
                continue
            
            has_remote = student[f'grade{grade}_covid'] == 1
            
            seteuk_analysis.append({
                'student_id': student_id,
                'grade': grade,
                'has_remote': 1 if has_remote else 0,
                'exploration_kw': grade_seteuk['kw_freq_exploration'].mean(),
                'online_kw': grade_seteuk['kw_freq_online'].mean(),
                'qualitative_kw': grade_seteuk['kw_freq_qualitative'].mean()
            })
    
    df_seteuk_analysis = pd.DataFrame(seteuk_analysis)
    
    if len(df_seteuk_analysis) == 0:
        print("  ⚠️  세특 데이터 부족")
        return
    
    # 1. 키워드 비교 (grouped bar)
    fig, ax = plt.subplots(figsize=(12, 6))
    
    no_remote = df_seteuk_analysis[df_seteuk_analysis['has_remote'] == 0]
    has_remote = df_seteuk_analysis[df_seteuk_analysis['has_remote'] == 1]
    
    keywords = ['Exploration', 'Online', 'Qualitative']
    no_remote_means = [
        no_remote['exploration_kw'].mean(),
        no_remote['online_kw'].mean(),
        no_remote['qualitative_kw'].mean()
    ]
    has_remote_means = [
        has_remote['exploration_kw'].mean(),
        has_remote['online_kw'].mean(),
        has_remote['qualitative_kw'].mean()
    ]
    
    x = np.arange(len(keywords))
    width = 0.35
    
    ax.bar(x - width/2, no_remote_means, width, label='No Remote', color='lightblue')
    ax.bar(x + width/2, has_remote_means, width, label='Has Remote', color='lightcoral')
    
    ax.set_ylabel('Keyword Frequency (per 1000 chars)', fontsize=12)
    ax.set_title('Keyword Frequency in Activity Details by Remote Learning',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(keywords)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'h1_2_keyword_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ h1_2_keyword_comparison.png")
    
    # 2. 변화율 시각화
    fig, ax = plt.subplots(figsize=(10, 6))
    
    changes = []
    for i, kw in enumerate(['exploration_kw', 'online_kw', 'qualitative_kw']):
        no_val = no_remote[kw].mean()
        has_val = has_remote[kw].mean()
        
        if no_val > 0:
            change_pct = ((has_val - no_val) / no_val) * 100
        else:
            change_pct = 0
        
        changes.append(change_pct)
    
    colors = ['red' if c < 0 else 'green' for c in changes]
    ax.barh(keywords, changes, color=colors, alpha=0.7)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Change (%)', fontsize=12)
    ax.set_title('Keyword Frequency Change with Remote Learning',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # 값 표시
    for i, (kw, val) in enumerate(zip(keywords, changes)):
        ax.text(val, i, f'{val:+.1f}%', va='center', 
                ha='left' if val > 0 else 'right', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'h1_2_keyword_change.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ h1_2_keyword_change.png")
    
    # 3. 학년별 온라인 키워드 추세
    fig, ax = plt.subplots(figsize=(12, 6))
    
    grade_online = []
    for grade in [1, 2, 3]:
        grade_data = df_seteuk_analysis[df_seteuk_analysis['grade'] == grade]
        
        no_remote_g = grade_data[grade_data['has_remote'] == 0]['online_kw'].mean()
        has_remote_g = grade_data[grade_data['has_remote'] == 1]['online_kw'].mean()
        
        grade_online.append({
            'Grade': grade,
            'No Remote': no_remote_g if not np.isnan(no_remote_g) else 0,
            'Has Remote': has_remote_g if not np.isnan(has_remote_g) else 0
        })
    
    df_online = pd.DataFrame(grade_online)
    
    ax.plot(df_online['Grade'], df_online['No Remote'], 
            marker='o', label='No Remote', linewidth=2, markersize=8, color='blue')
    ax.plot(df_online['Grade'], df_online['Has Remote'],
            marker='s', label='Has Remote', linewidth=2, markersize=8, color='red')
    
    ax.set_xlabel('Grade Level', fontsize=12)
    ax.set_ylabel('Online Keyword Frequency (per 1000 chars)', fontsize=12)
    ax.set_title('Online Keyword Frequency by Grade Level',
                 fontsize=14, fontweight='bold')
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(['Grade 1', 'Grade 2', 'Grade 3'])
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'h1_2_online_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ h1_2_online_trend.png")


def create_summary_figure(df_students, output_dir):
    """요약 시각화"""
    
    print("\n[요약 시각화]")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. 졸업년도 분포
    if 'hs_graduation_year' in df_students.columns:
        year_counts = df_students['hs_graduation_year'].value_counts().sort_index()
        axes[0, 0].bar(year_counts.index, year_counts.values, color='steelblue', alpha=0.7)
        axes[0, 0].set_xlabel('Graduation Year', fontsize=10)
        axes[0, 0].set_ylabel('Count', fontsize=10)
        axes[0, 0].set_title('High School Graduation Year Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].grid(axis='y', alpha=0.3)
    
    # 2. 코로나 경험
    if 'any_covid' in df_students.columns:
        covid_counts = df_students['any_covid'].value_counts()
        labels = ['No COVID', 'Has COVID']
        colors = ['lightcoral', 'lightblue']
        axes[0, 1].pie(covid_counts.values, labels=labels, colors=colors, 
                       autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('COVID-19 Exposure (Remote Learning)', fontsize=12, fontweight='bold')
    
    # 3. 학년별 코로나
    grade_covid = []
    for grade in [1, 2, 3]:
        col = f'grade{grade}_covid'
        if col in df_students.columns:
            count = (df_students[col] == 1).sum()
            grade_covid.append(count)
    
    if grade_covid:
        axes[1, 0].bar(['Grade 1', 'Grade 2', 'Grade 3'], grade_covid, 
                       color='coral', alpha=0.7)
        axes[1, 0].set_ylabel('Count', fontsize=10)
        axes[1, 0].set_title('Students with Remote Learning by Grade', fontsize=12, fontweight='bold')
        axes[1, 0].grid(axis='y', alpha=0.3)
    
    # 4. 재수 여부
    if 'is_repeat' in df_students.columns:
        repeat_counts = df_students['is_repeat'].value_counts()
        labels = ['Regular', 'Retaker']
        colors = ['lightgreen', 'lightyellow']
        axes[1, 1].pie(repeat_counts.values, labels=labels, colors=colors,
                       autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Student Type Distribution', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'summary_overview.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ summary_overview.png")


def main():
    """메인 함수"""
    
    print("\n" + "="*80)
    print("STEP 4: 시각화 생성")
    print("="*80)
    
    # 데이터 로드
    print("\n데이터 로딩 중...")
    try:
        df_students, df_grades, df_seteuk, df_volatility = load_data()
        print("✓ 데이터 로드 완료")
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        print("\n먼저 step1_final_complete.py를 실행하세요!")
        return
    
    # 출력 디렉토리
    output_dir = Path('outputs/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 시각화 생성
    create_h1_1_figures(df_students, df_grades, df_volatility, output_dir)
    create_h1_2_figures(df_students, df_seteuk, output_dir)
    create_summary_figure(df_students, output_dir)
    
    print("\n" + "="*80)
    print("✅ 시각화 완료!")
    print("="*80)
    print(f"\n📁 출력 위치: {output_dir}")
    print("\n생성된 파일:")
    print("  [H1-1]")
    print("    - h1_1_volatility_boxplot.png")
    print("    - h1_1_volatility_violin.png")
    print("    - h1_1_volatility_by_grade.png")
    print("  [H1-2]")
    print("    - h1_2_keyword_comparison.png")
    print("    - h1_2_keyword_change.png")
    print("    - h1_2_online_trend.png")
    print("  [요약]")
    print("    - summary_overview.png")

if __name__ == "__main__":
    main()