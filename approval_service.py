"""영업일지 결재 서비스 모듈"""

from utils.storage import load_data, save_data

SALES_REPORT_FILE = 'sales_reports'

# 허용된 상태 전이 매핑
_ALLOWED_TRANSITIONS = {
    'DRAFT': {'submit': 'SUBMITTED'},
    'SUBMITTED': {
        'approve': 'APPROVED',
        'reject': 'REJECTED',
        'withdraw': 'DRAFT',
    },
}


def _find_report(reports: list, report_id: str) -> int:
    """보고서 ID로 인덱스를 찾는다. 없으면 -1을 반환한다."""
    for i, r in enumerate(reports):
        if r.get('report_id') == report_id:
            return i
    return -1


def _transition(report_id: str, action: str) -> dict:
    """상태 전이를 수행한다.

    성공 시 {'success': True, 'data': {변경된영업일지}}를 반환한다.
    실패 시 {'success': False, 'error': '오류메시지'}를 반환한다.
    """
    reports = load_data(SALES_REPORT_FILE)
    idx = _find_report(reports, report_id)
    if idx == -1:
        return {'success': False,
                'error': f'보고서를 찾을 수 없습니다: {report_id}'}

    report = reports[idx]
    current_status = report.get('status', 'DRAFT')

    # 현재 상태에서 허용된 액션 조회
    allowed_actions = _ALLOWED_TRANSITIONS.get(current_status)
    if allowed_actions is None:
        return {'success': False,
                'error': f'"{current_status}" 상태에서는 결재 작업을 수행할 수 없습니다.'}

    new_status = allowed_actions.get(action)
    if new_status is None:
        return {'success': False,
                'error': f'"{current_status}" 상태에서 "{action}" 작업은 허용되지 않습니다.'}

    report['status'] = new_status

    if not save_data(SALES_REPORT_FILE, reports):
        return {'success': False, 'error': '파일 저장 중 오류가 발생했습니다.'}

    return {'success': True, 'data': report}


def submit_report(report_id: str) -> dict:
    """영업일지를 결재 상신한다. (DRAFT → SUBMITTED)"""
    return _transition(report_id, 'submit')


def approve_report(report_id: str) -> dict:
    """영업일지를 승인한다. (SUBMITTED → APPROVED)"""
    return _transition(report_id, 'approve')


def reject_report(report_id: str) -> dict:
    """영업일지를 반려한다. (SUBMITTED → REJECTED)"""
    return _transition(report_id, 'reject')


def withdraw_report(report_id: str) -> dict:
    """영업일지 결재를 철회한다. (SUBMITTED → DRAFT)"""
    return _transition(report_id, 'withdraw')