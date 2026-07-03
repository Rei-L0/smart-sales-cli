"""영업일지 관리 서비스 모듈"""

from utils.storage import load_data, save_data
from utils.validators import (
    validate_report_id,
    validate_date,
    validate_content,
)
from customer_service import get_customer

SALES_REPORT_FILE = 'sales_reports'


def _find_report(reports: list, report_id: str) -> int:
    """보고서 ID로 인덱스를 찾는다. 없으면 -1을 반환한다."""
    for i, r in enumerate(reports):
        if r.get('report_id') == report_id:
            return i
    return -1


def create_report(report_id: str, customer_id: str,
                  date: str, content: str) -> dict:
    """영업일지를 등록한다.
    
    성공 시 {'success': True, 'data': {영업일지정보}}를 반환한다.
    실패 시 {'success': False, 'error': '오류메시지'}를 반환한다.
    """
    # 입력값 검증
    err = validate_report_id(report_id)
    if err:
        return {'success': False, 'error': err}
    err = validate_customer_id_for_report(customer_id)
    if err:
        return {'success': False, 'error': err}
    err = validate_date(date)
    if err:
        return {'success': False, 'error': err}
    err = validate_content(content)
    if err:
        return {'success': False, 'error': err}

    # 고객사 존재 확인
    customer_result = get_customer(customer_id)
    if not customer_result['success']:
        return {'success': False,
                'error': f'존재하지 않는 고객사입니다: {customer_id}'}

    reports = load_data(SALES_REPORT_FILE)

    # 중복 ID 체크
    if _find_report(reports, report_id) != -1:
        return {'success': False, 'error': f'이미 등록된 보고서 ID입니다: {report_id}'}

    new_report = {
        'report_id': report_id,
        'customer_id': customer_id,
        'date': date.strip(),
        'content': content.strip(),
        'status': 'DRAFT',
    }
    reports.append(new_report)

    if not save_data(SALES_REPORT_FILE, reports):
        return {'success': False, 'error': '파일 저장 중 오류가 발생했습니다.'}

    return {'success': True, 'data': new_report}


def validate_customer_id_for_report(customer_id: str) -> str:
    """영업일지 등록용 고객사 ID 필수 입력 검증."""
    customer_id = customer_id.strip()
    if not customer_id:
        return '고객사 ID를 입력해주세요.'
    return ''


def list_reports() -> dict:
    """영업일지 목록을 조회한다."""
    reports = load_data(SALES_REPORT_FILE)
    return {'success': True, 'data': reports}


def get_report(report_id: str) -> dict:
    """영업일지 상세 정보를 조회한다."""
    reports = load_data(SALES_REPORT_FILE)
    idx = _find_report(reports, report_id)
    if idx == -1:
        return {'success': False, 'error': f'보고서를 찾을 수 없습니다: {report_id}'}
    return {'success': True, 'data': reports[idx]}


def update_report(report_id: str, date: str, content: str) -> dict:
    """영업일지 정보를 수정한다.
    
    APPROVED 상태인 영업일지는 수정할 수 없다.
    """
    reports = load_data(SALES_REPORT_FILE)
    idx = _find_report(reports, report_id)
    if idx == -1:
        return {'success': False, 'error': f'보고서를 찾을 수 없습니다: {report_id}'}

    # APPROVED 상태 차단
    if reports[idx].get('status') == 'APPROVED':
        return {'success': False,
                'error': '승인된 영업일지는 수정할 수 없습니다.'}

    # 입력값 검증
    err = validate_date(date)
    if err:
        return {'success': False, 'error': err}
    err = validate_content(content)
    if err:
        return {'success': False, 'error': err}

    reports[idx]['date'] = date.strip()
    reports[idx]['content'] = content.strip()

    if not save_data(SALES_REPORT_FILE, reports):
        return {'success': False, 'error': '파일 저장 중 오류가 발생했습니다.'}

    return {'success': True, 'data': reports[idx]}