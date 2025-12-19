"""
STEP 1 (수정 완료본): 생활기록부 파싱 (성적은 엑셀에서 로드)
- TXT에서는 학생기본정보 + 원격수업일수(코로나) + 세특만 추출
- 성적은 이미 정리된 엑셀(학생_성적_정보_양식_통합.xlsx)에서 읽어 df_grades로 사용
- 완전 호환 CSV 생성 + 상세 엑셀 보고서 생성
"""

import os
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
import warnings
warnings.filterwarnings("ignore")


class FinalParser:
    """최종 완성 파서 (성적 파싱 제거 버전)"""

    def __init__(self):
        # 교육부 공식 과목 리스트
        self.all_subjects = [
            '공통국어1', '공통국어2', '공통수학1', '공통수학2', '공통영어1', '공통영어2',
            '한국사1', '한국사2', '통합사회1', '통합사회2', '통합과학1', '통합과학2',
            '과학탐구실험1', '과학탐구실험2', '기본수학1', '기본수학2', '기본영어1', '기본영어2',
            '국어', '수학', '영어', '한국사', '통합사회', '통합과학', '과학탐구실험',
            '화법과 작문', '독서', '언어와 매체', '문학', '실용 국어', '심화 국어',
            '고전 읽기', '화법과 언어', '독서와 작문', '주제 탐구 독서', '문학과 영상',
            '직무 의사소통', '독서 토론과 글쓰기', '매체 의사소통', '언어생활 탐구',
            '수학Ⅰ', '수학Ⅱ', '미적분', '확률과 통계', '실용 수학', '기하', '경제 수학',
            '수학과제 탐구', '기본 수학', '인공지능 수학', '대수', '미적분I', '미적분II',
            '직무 수학', '수학과 문화', '실용 통계', '수학 1', '수학 I', '수학 II',
            '영어회화', '영어Ⅰ', '영어독해와 작문', '영어Ⅱ', '실용영어', '영어권 문화',
            '진로 영어', '영미 문학 읽기', '기본 영어', '영어 발표와 토론', '심화 영어',
            '심화 영어 독해와 작문', '직무 영어', '실생활 영어 회화', '미디어 영어',
            '세계 문화와 영어', '실용 영어회화', '실용영어 I', '영어 II', '영어 I',
            '한국지리', '세계지리', '세계사', '동아시아사', '경제', '정치와 법', '사회·문화',
            '생활과 윤리', '윤리와 사상', '여행지리', '사회문제 탐구', '고전과 윤리',
            '세계시민과 지리', '현대사회와 윤리', '한국지리 탐구', '도시의 미래 탐구',
            '동아시아 역사 기행', '법과 사회', '인문학과 윤리', '국제 관계의 이해',
            '역사로 탐구하는 현대 세계', '금융과 경제생활', '윤리문제 탐구',
            '기후변화와 지속가능한 세계', '사회', '현대 세계의 변화',
            '물리학Ⅰ', '화학Ⅰ', '생명과학Ⅰ', '지구과학Ⅰ', '물리학Ⅱ', '화학Ⅱ',
            '생명과학Ⅱ', '지구과학Ⅱ', '과학사', '생활과 과학', '융합과학', '과학',
            '물리학 I', '화학 I', '생명과학 I', '지구과학 I',
            '체육', '운동과 건강', '스포츠 생활', '체육 탐구',
            '음악', '미술', '연극', '음악 연주', '음악 감상과 비평',
            '미술 창작', '미술 감상과 비평',
            '기술·가정', '정보', '농업 생명 과학', '공학 일반', '창의 경영',
            '해양 문화와 기술', '가정과학', '지식 재산 일반', '인공지능 기초', '철학', '기술 . 가정',
            '독일어I', '프랑스어I', '스페인어I', '중국어I', '일본어I', '러시아어I',
            '아랍어I', '베트남어I', '독일어II', '프랑스어II', '스페인어II', '중국어II',
            '일본어II', '러시아어II', '아랍어II', '베트남어II', '일본어 I',
            '한문I', '한문II', '한문 I', '한문 [', '철학', '논리학', '심리학', '교육학', '종교학',
            '진로와 직업', '보건', '환경', '실용 경제', '논술', '안전한 생활'
        ]

        # 교과군 매핑
        self.subject_to_group = {}
        for subject in self.all_subjects:
            if any(kw in subject for kw in ['국어', '화법', '작문', '독서', '언어', '매체', '문학', '고전', '의사소통', '글쓰기']):
                self.subject_to_group[subject] = '국어'
            elif any(kw in subject for kw in ['수학', '미적분', '확률', '통계', '기하', '대수']):
                self.subject_to_group[subject] = '수학'
            elif any(kw in subject for kw in ['영어', 'English']):
                self.subject_to_group[subject] = '영어'
            elif any(kw in subject for kw in ['역사', '한국사', '세계사', '동아시아', '지리', '경제', '정치', '법', '사회', '윤리', '도덕', '현대']):
                self.subject_to_group[subject] = '사회'
            elif any(kw in subject for kw in ['과학', '물리', '화학', '생명', '지구', '생태', '환경', '융합과학', '탐구실험', '탐구실']):
                self.subject_to_group[subject] = '과학'
            elif any(kw in subject for kw in ['체육', '운동', '스포츠']):
                self.subject_to_group[subject] = '체육'
            elif any(kw in subject for kw in ['음악', '미술', '연극', '예술']):
                self.subject_to_group[subject] = '예술'
            elif any(kw in subject for kw in ['기술', '가정', '정보', '농업', '공학']):
                self.subject_to_group[subject] = '기술·가정'
            elif any(kw in subject for kw in ['독일어', '프랑스어', '스페인어', '중국어', '일본어', '러시아어', '아랍어', '베트남어']):
                self.subject_to_group[subject] = '제2외국어'
            else:
                self.subject_to_group[subject] = '교양'

        # 키워드
        self.exploration_keywords = [
            '실험', '실습', '관찰', '측정', '분석', '탐구', '연구', '조사',
            '탐색', '발견', '현장', '답사', '견학', '방문', '체험', '실사',
            '프로젝트', '과제연구', '팀프로젝트', '모둠활동', '소집단',
            '가설', '검증', '실험설계', '데이터수집', '결과분석', '보고서작성',
            '모둠', '팀', '조별', '협력', '협동', '그룹', '공동연구'
        ]

        self.online_keywords = [
            '온라인', '원격', '비대면', '화상', '실시간', '쌍방향',
            'zoom', '줌', 'ZOOM', '구글클래스룸', '클래스룸', 'e-학습터',
            '이학습터', 'EBS', 'ebs', '위두랑',
            '디지털', '인터넷', '웹', '앱', '플랫폼', '사이버',
            '원격수업', '온라인수업', '화상수업', '원격활동', '온라인활동',
            '동영상', '영상', '온라인자료', '디지털자료', '전자교과서'
        ]

        self.qualitative_keywords = [
            '과정', '노력', '태도', '참여', '열정', '몰입', '집중',
            '협력', '협동', '배려', '나눔', '소통', '공감', '존중',
            '성장', '발전', '개선', '극복', '도전', '변화', '진보',
            '관심', '흥미', '호기심', '탐구심', '의지'
        ]

    def extract_all_years_from_text(self, text: str) -> List[int]:
        """텍스트 전체에서 모든 연도 추출"""
        all_years = []
        patterns = [
            r'(20\d{2})[\.,\-/]\s*\d{2}[\.,\-/]\s*\d{2}',
            r'\((20\d{2})\)',
            r'(20\d{2})년',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    year = int(match)
                    if 2010 <= year <= 2025:
                        all_years.append(year)
                except:
                    pass

        return all_years

    def estimate_graduation_year_from_frequency(self, text: str) -> Tuple[int, str]:
        """빈도 분석으로 졸업년도 추정"""
        all_years = self.extract_all_years_from_text(text)

        if not all_years:
            return None, '추정불가'

        year_counter = Counter(all_years)
        most_common = year_counter.most_common()
        top_years = [year for year, _ in most_common[:3]]

        if len(top_years) >= 2:
            estimated_admission = min(top_years)
            estimated_graduation = estimated_admission + 3
            return estimated_graduation, '빈도분석'
        else:
            return top_years[0], '빈도분석'

    def extract_remote_days(self, text: str) -> Dict[int, int]:
        """학년별 원격수업일수 추출 (강화된 패턴)"""
        remote_days = {}

        patterns = [
            r'원격\s*수업\s*일수?\s*(\d+)\s*일',
            r'원격\s*일수?\s*(\d+)\s*일',
            r'인격\s*수업\s*일수?\s*(\d+)\s*일',
            r'원격\s*수입\s*일수?\s*(\d+)\s*일',
            r'인격\s*수입\s*일수?\s*(\d+)\s*일',
            r'원격수업일수(\d+)일',
            r'인격수업일수(\d+)일',
            r'원격수입일수(\d+)일',
            r'원격\s*수업\s*일수?\s*(\d+)',
            r'원격\s*일수?\s*(\d+)',
            r'인격\s*수업\s*일수?\s*(\d+)',
            r'원격\s*수입\s*일수?\s*(\d+)',
            r'개근\s*,?\s*원격\s*수업?\s*일수?\s*(\d+)\s*일',
            r'개근\s*\.?\s*원격\s*수업?\s*일수?\s*(\d+)\s*일',
            r'개근\s*원격\s*수업?\s*일수?\s*(\d+)\s*일',
        ]

        all_remote_values = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = int(match)
                    if 0 <= value <= 200:
                        all_remote_values.append(value)
                except:
                    pass

        sections = re.split(r'\[(\d)학년\]', text)

        for i in range(len(sections)):
            section = sections[i].strip()

            if re.match(r'^\d$', section):
                continue

            if i > 0 and re.match(r'^\d$', sections[i - 1]):
                grade = int(sections[i - 1])

                section_values = []
                for pattern in patterns:
                    matches = re.findall(pattern, section, re.IGNORECASE)
                    for match in matches:
                        try:
                            value = int(match)
                            if 0 <= value <= 200:
                                section_values.append(value)
                        except:
                            pass

                if section_values:
                    remote_days[grade] = max(section_values)

        # fallback
        if not remote_days and all_remote_values:
            non_zero_values = [v for v in all_remote_values if v > 0]
            if non_zero_values:
                sorted_values = sorted(set(non_zero_values), reverse=True)[:3]
                for idx, grade in enumerate([3, 2, 1]):
                    if idx < len(sorted_values):
                        remote_days[grade] = sorted_values[idx]

        return remote_days

    def parse_student_info(self, text: str, filename: str) -> Dict:
        """학생 기본 정보 추출 (빈도 분석만 사용)"""
        info = {}

        patterns = [
            r'(\d{9})_(\d)학?년?_(.+?)_(.+?)_(수시|정시)',
            r'(\d{9})_(\d)_(.+?)_(.+?)_(수시|정시)',
            r'(\d{9})_(\d)학?년?_(.+?)_(.+?)_censored'
        ]

        match = None
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                break

        if not match:
            return {}

        info['student_id'] = match.group(1)
        info['name'] = match.group(4)
        info['major'] = match.group(3)
        info['admission_type'] = match.group(5) if len(match.groups()) >= 5 else '불명'
        info['university_admission_year'] = int(info['student_id'][:4])

        estimated_grad, method = self.estimate_graduation_year_from_frequency(text)

        if estimated_grad:
            hs_admission = estimated_grad - 3
            full_grade_years = {1: hs_admission, 2: hs_admission + 1, 3: hs_admission + 2}
            info['hs_graduation_year'] = estimated_grad
            info['estimation_method'] = method
        else:
            hs_admission = info['university_admission_year'] - 3
            full_grade_years = {1: hs_admission, 2: hs_admission + 1, 3: hs_admission + 2}
            info['hs_graduation_year'] = info['university_admission_year']
            info['estimation_method'] = '실패(현역가정)'

        info['grade_years'] = full_grade_years

        gap = info['university_admission_year'] - info['hs_graduation_year']
        if gap > 0:
            info['is_repeat'] = 1
            info['repeat_years'] = gap
        else:
            info['is_repeat'] = 0
            info['repeat_years'] = 0

        remote_days = self.extract_remote_days(text)
        info['remote_days'] = remote_days

        info['grade1_covid'] = 1 if remote_days.get(1, 0) > 0 else 0
        info['grade2_covid'] = 1 if remote_days.get(2, 0) > 0 else 0
        info['grade3_covid'] = 1 if remote_days.get(3, 0) > 0 else 0
        info['any_covid'] = 1 if any(remote_days.values()) else 0

        info['cohort'] = 'COVID' if info['hs_graduation_year'] >= 2021 else 'Pre-COVID'
        return info

    def identify_subject_group(self, subject_name: str) -> str:
        """과목명으로 교과군 찾기"""
        normalized = subject_name.strip()

        if normalized in self.subject_to_group:
            return self.subject_to_group[normalized]

        normalized2 = re.sub(r'[\s\-·]', '', normalized)
        for subject, group in self.subject_to_group.items():
            subject_normalized = re.sub(r'[\s\-·]', '', subject)
            if normalized2 == subject_normalized:
                return group

        # fallback: 키워드 기반 간단 판정
        if any(k in normalized for k in ['국어', '문학', '독서', '화법', '작문', '언어', '매체']):
            return '국어'
        if any(k in normalized for k in ['수학', '미적분', '확률', '통계', '기하', '대수']):
            return '수학'
        if '영어' in normalized or 'English' in normalized:
            return '영어'
        if any(k in normalized for k in ['사회', '윤리', '경제', '정치', '법', '지리', '역사']):
            return '사회'
        if any(k in normalized for k in ['과학', '물리', '화학', '생명', '지구']):
            return '과학'

        return '기타'

    def extract_seteuk(self, text: str, student_id: str, grade_years: Dict[int, int]) -> List[Dict]:
        """세부능력 특기사항 추출"""
        seteuk_list = []

        grade_sections = re.split(r'\[(\d)학년\]', text)
        current_grade = None

        for i in range(len(grade_sections)):
            section = grade_sections[i].strip()

            if re.match(r'^\d$', section):
                current_grade = int(section)
                continue

            if current_grade is None:
                continue

            year = grade_years.get(current_grade, None)

            pattern = r'\((\d)학기\)\s*([가-힣\s\d.·I-ⅡIII]+?):\s*(.+?)(?=\(\d학기\)|$)'
            matches = re.finditer(pattern, section, re.DOTALL)

            for match in matches:
                term = int(match.group(1))
                subject = match.group(2).strip()
                content = match.group(3).strip()

                # 줄 단위 정리
                content_lines = []
                for line in content.split('\n'):
                    if re.match(r'\(\d학기\)\s*[가-힣\s\d.]+?:|<.*?>|^\d+\.|이수단위|체육|예술', line.strip()):
                        break
                    content_lines.append(line)

                content = ' '.join(content_lines).strip()

                if len(content) < 50:
                    continue

                exploration_count = sum(1 for kw in self.exploration_keywords if kw in content)
                online_count = sum(1 for kw in self.online_keywords if kw in content)
                qualitative_count = sum(1 for kw in self.qualitative_keywords if kw in content)

                seteuk_list.append({
                    'student_id': student_id,
                    'grade_year': current_grade,
                    'year': year,
                    'term': term,
                    'subject': subject,
                    'subject_group': self.identify_subject_group(subject),
                    'content': content,
                    'content_length': len(content),
                    'exploration_keyword_count': exploration_count,
                    'online_keyword_count': online_count,
                    'qualitative_keyword_count': qualitative_count,
                    'kw_freq_exploration': exploration_count / len(content) * 1000,
                    'kw_freq_online': online_count / len(content) * 1000,
                    'kw_freq_qualitative': qualitative_count / len(content) * 1000
                })

        return seteuk_list


def load_grades_from_excel(excel_path: str) -> pd.DataFrame:
    """이미 정리된 성적 엑셀을 df_grades(표준 컬럼)로 로드"""
    df = pd.read_excel(excel_path)

    # 샘플 행(열1~열11 등) 제거: 학번이 9자리 숫자인 행만 유지
    df = df[df['학번'].astype(str).str.fullmatch(r'\d{9}')].copy()

    # 표준 컬럼명으로 변경
    df = df.rename(columns={
        '학번': 'student_id',
        '학년': 'grade_year',
        '연도': 'year',
        '학기': 'term',
        '과목': 'subject',
        '교과군': 'subject_group',
        '등급': 'achievement',
        '평가방식': 'grade_type',
        '원점수': 'raw_score',
        '과목평균': 'subject_avg',
        '표준편차': 'std_dev'
    })

    # 평가방식 정규화
    df['grade_type'] = df['grade_type'].replace({'절대평가': 'achievement', '상대평가': 'rank'})

    # 등급/타입 정리
    df['achievement'] = df['achievement'].astype(str).str.strip()

    # grade_numeric 생성 (변동성 계산용)
    grade_map_achievement = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    grade_map_rank = {str(i): i for i in range(1, 10)}

    def to_numeric(row):
        gtype = row.get('grade_type', '')
        ach = str(row.get('achievement', '')).strip()
        if gtype == 'achievement':
            return grade_map_achievement.get(ach, 0)
        return grade_map_rank.get(ach, 0)

    df['grade_numeric'] = df.apply(to_numeric, axis=1)

    # 숫자형 정리(깨진 값은 NaN -> Int64)
    for col in ['grade_year', 'year', 'term']:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    for col in ['raw_score', 'subject_avg', 'std_dev']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def calculate_volatility_from_df(df_grades: pd.DataFrame, student_id: str, remote_days: Dict[int, int]) -> Dict:
    """df_grades(엑셀 기반)에서 학생 1명의 성적 변동성 계산"""
    metrics = {'student_id': student_id}

    df = df_grades[df_grades['student_id'].astype(str) == str(student_id)].copy()
    if df.empty:
        return metrics

    # 전체
    valid_all = df[df['grade_numeric'] > 0]['grade_numeric']
    if len(valid_all) > 1:
        metrics['overall_volatility'] = valid_all.std()
        metrics['overall_mean'] = valid_all.mean()

    # 절대/상대
    df_achievement = df[df['grade_type'] == 'achievement']
    valid = df_achievement[df_achievement['grade_numeric'] > 0]['grade_numeric']
    if len(valid) > 1:
        metrics['achievement_volatility'] = valid.std()
        metrics['achievement_mean'] = valid.mean()

    df_rank = df[df['grade_type'] == 'rank']
    valid = df_rank[df_rank['grade_numeric'] > 0]['grade_numeric']
    if len(valid) > 1:
        metrics['rank_volatility'] = valid.std()
        metrics['rank_mean'] = valid.mean()

    # 학년별
    for grade in [1, 2, 3]:
        gd = df[df['grade_year'] == grade]
        valid_g = gd[gd['grade_numeric'] > 0]['grade_numeric']
        if len(valid_g) > 1:
            metrics[f'grade{grade}_volatility'] = valid_g.std()
            metrics[f'grade{grade}_mean'] = valid_g.mean()
        metrics[f'grade{grade}_covid'] = 1 if remote_days.get(grade, 0) > 0 else 0

    return metrics


def create_detailed_excel(df_students, df_grades, df_seteuk, output_path='data/results/학생별_상세정보.xlsx'):
    """상세 엑셀 생성"""
    print("\n상세 엑셀 보고서 생성 중...")

    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            print(f"  기존 엑셀 파일 삭제: {output_path}")
        except Exception:
            print("  엑셀 파일이 열려있습니다.")
            print(f"  {output_path} 파일을 닫고 다시 실행하세요.")
            return False

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1) 학생 기본정보
            basic_cols = [
                'student_id', 'name', 'major', 'admission_type',
                'university_admission_year', 'hs_graduation_year',
                'is_repeat', 'repeat_years', 'any_covid', 'cohort', 'estimation_method'
            ]
            df_basic = df_students[basic_cols].copy()
            df_basic.columns = ['학번', '이름', '전공', '입학전형', '대학입학년도', '고교졸업년도',
                                '재수여부', '재수년수', '코로나경험', '코호트', '추정방법']
            df_basic['재수여부'] = df_basic['재수여부'].map({0: '현역', 1: '재수생'})
            df_basic['코로나경험'] = df_basic['코로나경험'].map({0: '없음', 1: '있음'})
            df_basic.to_excel(writer, sheet_name='학생기본정보', index=False)

            # 2) 학년별 코로나
            covid_data = []
            for _, row in df_students.iterrows():
                for grade in [1, 2, 3]:
                    covid_data.append({
                        '학번': row['student_id'],
                        '이름': row['name'],
                        '학년': grade,
                        '연도': row['grade_years'].get(grade) if isinstance(row.get('grade_years'), dict) else None,
                        '원격일수': row['remote_days'].get(grade, 0) if isinstance(row.get('remote_days'), dict) else 0,
                        '코로나여부': row.get(f'grade{grade}_covid', 0)
                    })
            df_covid = pd.DataFrame(covid_data)
            df_covid['코로나여부'] = df_covid['코로나여부'].map({0: '없음', 1: '있음'})
            df_covid.to_excel(writer, sheet_name='학년별코로나', index=False)

            # 3) 전체성적 (표준편차 포함)
            grade_cols = [
                'student_id', 'grade_year', 'year', 'term',
                'subject', 'subject_group', 'achievement', 'grade_type',
                'raw_score', 'subject_avg', 'std_dev'
            ]
            existing_cols = [c for c in grade_cols if c in df_grades.columns]
            df_grade_out = df_grades[existing_cols].copy()

            rename_out = {
                'student_id': '학번',
                'grade_year': '학년',
                'year': '연도',
                'term': '학기',
                'subject': '과목',
                'subject_group': '교과군',
                'achievement': '등급',
                'grade_type': '평가방식',
                'raw_score': '원점수',
                'subject_avg': '과목평균',
                'std_dev': '표준편차'
            }
            df_grade_out = df_grade_out.rename(columns=rename_out)
            if '평가방식' in df_grade_out.columns:
                df_grade_out['평가방식'] = df_grade_out['평가방식'].map({'achievement': '절대평가', 'rank': '상대평가'}).fillna(df_grade_out['평가방식'])
            df_grade_out.to_excel(writer, sheet_name='전체성적', index=False)

            # 4) 학기별 이수과목수
            if not df_grades.empty and all(c in df_grades.columns for c in ['student_id', 'grade_year', 'term']):
                course_count = df_grades.groupby(['student_id', 'grade_year', 'term']).size().reset_index(name='이수과목수')
                course_count = course_count.merge(df_students[['student_id', 'name']], on='student_id', how='left')
                course_count = course_count[['student_id', 'name', 'grade_year', 'term', '이수과목수']]
                course_count.columns = ['학번', '이름', '학년', '학기', '이수과목수']
                course_count.to_excel(writer, sheet_name='학기별이수과목수', index=False)

            # 5) 세특개수
            if not df_seteuk.empty:
                seteuk_count = df_seteuk.groupby('student_id').size().reset_index(name='세특섹션개수')
                seteuk_count = seteuk_count.merge(df_students[['student_id', 'name']], on='student_id', how='left')
                seteuk_count = seteuk_count[['student_id', 'name', '세특섹션개수']]
                seteuk_count.columns = ['학번', '이름', '세특섹션개수']
                seteuk_count.to_excel(writer, sheet_name='세특개수', index=False)

            # 6) 학생별 등급분포
            grade_dist_data = []
            for sid in df_students['student_id'].unique():
                student_grades = df_grades[df_grades['student_id'].astype(str) == str(sid)]
                if len(student_grades) == 0:
                    continue

                student_name = df_students[df_students['student_id'] == sid]['name'].iloc[0] if (df_students['student_id'] == sid).any() else ''

                ach_grades = student_grades[student_grades['grade_type'] == 'achievement']
                ach_dist = ach_grades['achievement'].value_counts().to_dict()

                rank_grades = student_grades[student_grades['grade_type'] == 'rank']
                rank_dist = rank_grades['achievement'].value_counts().to_dict()

                grade_dist_data.append({
                    '학번': sid,
                    '이름': student_name,
                    'A등급': ach_dist.get('A', 0),
                    'B등급': ach_dist.get('B', 0),
                    'C등급': ach_dist.get('C', 0),
                    'D등급': ach_dist.get('D', 0),
                    'E등급': ach_dist.get('E', 0),
                    '1등급': rank_dist.get('1', 0),
                    '2등급': rank_dist.get('2', 0),
                    '3등급': rank_dist.get('3', 0),
                    '4등급': rank_dist.get('4', 0),
                    '5등급': rank_dist.get('5', 0),
                    '6등급': rank_dist.get('6', 0),
                    '7등급': rank_dist.get('7', 0),
                    '8등급': rank_dist.get('8', 0),
                    '9등급': rank_dist.get('9', 0),
                })

            if grade_dist_data:
                pd.DataFrame(grade_dist_data).to_excel(writer, sheet_name='학생별등급분포', index=False)

        print(f"  엑셀 저장 성공: {output_path}")
        return True

    except Exception as e:
        print(f"  엑셀 저장 실패: {e}")
        return False


def main():
    print("=" * 80)
    print("STEP 1: 수정본 (성적=엑셀 로드 / TXT=학생정보+세특+원격일수)")
    print("=" * 80)

    # ✅ 네 환경에 맞게 조정
    input_dir = Path('data/raw')  # 생활기록부 txt 폴더
    grades_excel_path = Path('data/raw/학생_성적_정보_양식_통합.xlsx')  # 성적 엑셀 파일
    output_dir = Path('data/processed')
    results_dir = Path('data/results')
    logs_dir = Path('logs')

    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    txt_files = list(input_dir.glob('*.txt'))
    print(f"\n총 {len(txt_files)}개 TXT 파일 발견")

    if len(txt_files) == 0:
        print("data/raw/ 디렉토리에 txt 파일이 없습니다.")
        return

    if not grades_excel_path.exists():
        print(f"\n[중단] 성적 엑셀 파일이 없습니다: {grades_excel_path}")
        print("성적 엑셀을 위 경로에 두거나 grades_excel_path를 수정하세요.")
        return

    parser = FinalParser()

    all_student_info = []
    all_seteuk = []
    parsing_errors = []

    print("\n파싱 진행 중 (TXT: 학생정보/세특/원격일수)...")
    for i, filepath in enumerate(txt_files, 1):
        print(f"  [{i}/{len(txt_files)}] {filepath.name}...", end=' ')
        try:
            filename = filepath.name
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            student_info = parser.parse_student_info(text, filename)
            if not student_info:
                parsing_errors.append(f"{filename}: 학생정보 파싱 실패")
                print("실패")
                continue

            student_id = student_info['student_id']
            grade_years = student_info['grade_years']

            all_student_info.append(student_info)

            seteuk = parser.extract_seteuk(text, student_id, grade_years)
            all_seteuk.extend(seteuk)

            print("완료")

        except Exception as e:
            parsing_errors.append(f"{filepath.name}: {str(e)}")
            print("오류")

    print("\n성적 로드 중 (엑셀)...")
    df_grades = load_grades_from_excel(str(grades_excel_path))
    print(f"  성적 건수: {len(df_grades)}")

    print("\n데이터프레임 생성/저장 중...")
    df_students = pd.DataFrame(all_student_info)
    df_seteuk = pd.DataFrame(all_seteuk)

    # volatility 생성 (엑셀 성적 기반)
    all_volatility = []
    for _, row in df_students.iterrows():
        sid = row['student_id']
        remote_days = row.get('remote_days', {})
        if not isinstance(remote_days, dict):
            remote_days = {}
        all_volatility.append(calculate_volatility_from_df(df_grades, sid, remote_days))
    df_volatility = pd.DataFrame(all_volatility)

    csv_files = {
        'student_info.csv': df_students,
        'grades.csv': df_grades,
        'seteuk.csv': df_seteuk,
        'volatility.csv': df_volatility
    }

    for filename, dataframe in csv_files.items():
        filepath = output_dir / filename

        if filepath.exists():
            try:
                os.remove(filepath)
                print(f"  기존 파일 삭제: {filename}")
            except Exception as e:
                print(f"  {filename} 삭제 실패: {e}")
                print("  파일을 닫고 다시 실행하세요.")
                return

        try:
            dataframe.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"  저장: {filename}")
        except Exception as e:
            print(f"  {filename} 저장 실패: {e}")
            return

    # 상세 엑셀 생성
    create_detailed_excel(df_students, df_grades, df_seteuk)

    print("\n" + "=" * 80)
    print("파싱 완료")
    print("=" * 80)

    print(f"\n학생 정보: {len(df_students)}명")
    if 'is_repeat' in df_students.columns:
        print(f"   - 현역: {(df_students['is_repeat'] == 0).sum()}명")
        print(f"   - 재수생: {(df_students['is_repeat'] == 1).sum()}명")

    print(f"\n성적 데이터(엑셀 기반): {len(df_grades)}건")
    if 'grade_type' in df_grades.columns:
        ach = (df_grades['grade_type'] == 'achievement').sum()
        rank = (df_grades['grade_type'] == 'rank').sum()
        print(f"   - 절대평가: {ach}건")
        print(f"   - 상대평가: {rank}건")

    print(f"\n세특 데이터: {len(df_seteuk)}건")
    print(f"변동성 데이터: {len(df_volatility)}건")

    if 'estimation_method' in df_students.columns:
        print("\n졸업년도 추정 방법:")
        for method, count in df_students['estimation_method'].value_counts().items():
            print(f"   - {method}: {count}명")

    if 'any_covid' in df_students.columns:
        print("\n코로나 경험:")
        print(f"   - 있음: {(df_students['any_covid'] == 1).sum()}명")
        print(f"   - 없음: {(df_students['any_covid'] == 0).sum()}명")

    print("\n학년별 코로나 경험:")
    for grade in [1, 2, 3]:
        col = f'grade{grade}_covid'
        if col in df_students.columns:
            print(f"   - {grade}학년: {(df_students[col] == 1).sum()}명")

    if 'hs_graduation_year' in df_students.columns:
        print("\n고교 졸업년도 분포:")
        for year, count in df_students['hs_graduation_year'].value_counts().sort_index().items():
            print(f"   {year}년: {count}명")

    if parsing_errors:
        print(f"\n오류 {len(parsing_errors)}개 (logs/parsing_errors.log 저장)")
        with open(logs_dir / 'parsing_errors.log', 'w', encoding='utf-8') as f:
            f.write('\n'.join(parsing_errors))

    print("\n저장 위치:")
    print("  - CSV: data/processed/")
    print("  - 엑셀: data/results/학생별_상세정보.xlsx")
    print("\nStep 1 완료")


if __name__ == "__main__":
    main()
