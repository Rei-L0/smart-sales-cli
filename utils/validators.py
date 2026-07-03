"""입력값 검증 함수 모듈

현재 단계: 빈 함수 뼈대만 정의.
이후 단계에서 실제 검증 로직을 구현한다.
"""


import re


def validate_customer_id(value: str) -> str:
    """고객사 ID 형식을 검증한다. 형식: C001, C002 등"""
    value = value.strip()
    if not value:
        return '고객사 ID를 입력해주세요.'
    if not re.match(r'^C\d{3}$', value):
        return '고객사 ID는 "C" 뒤에 숫자 3자리여야 합니다. (예: C001)'
    return ''


def validate_customer_name(value: str) -> str:
    """고객사명 필수 입력을 검증한다."""
    value = value.strip()
    if not value:
        return '고객사명을 입력해주세요.'
    return ''


def validate_manager_name(value: str) -> str:
    """담당자명 필수 입력을 검증한다."""
    value = value.strip()
    if not value:
        return '담당자명을 입력해주세요.'
    return ''


def validate_email(value: str) -> str:
    """이메일 형식을 검증한다."""
    value = value.strip()
    if not value:
        return '이메일을 입력해주세요.'
    if '@' not in value or '.' not in value:
        return '올바른 이메일 형식이 아닙니다. (예: name@example.com)'
    return ''


def validate_date(value: str) -> str:
    """날짜 형식(YYYY-MM-DD)을 검증한다."""
    value = value.strip()
    if not value:
        return '날짜를 입력해주세요.'
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
        return '날짜는 YYYY-MM-DD 형식이어야 합니다. (예: 2026-01-01)'
    try:
        import datetime
        datetime.datetime.strptime(value, '%Y-%m-%d')
        return ''
    except ValueError:
        return '존재하지 않는 날짜입니다.'


def validate_content(value: str) -> str:
    """영업일지 내용 필수 입력을 검증한다."""
    value = value.strip()
    if not value:
        return '영업일지 내용을 입력해주세요.'
    return ''


def validate_report_id(value: str) -> str:
    """보고서 ID 형식을 검증한다. 형식: R001, R002 등"""
    value = value.strip()
    if not value:
        return '보고서 ID를 입력해주세요.'
    if not re.match(r'^R\d{3}$', value):
        return '보고서 ID는 "R" 뒤에 숫자 3자리여야 합니다. (예: R001)'
    return ''
