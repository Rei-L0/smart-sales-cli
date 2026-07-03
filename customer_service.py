"""고객사 관리 서비스 모듈"""

from utils.storage import load_data, save_data
from utils.validators import (
    validate_customer_id,
    validate_customer_name,
    validate_manager_name,
    validate_email,
)

CUSTOMER_FILE = 'customers'


def _find_customer(customers: list, customer_id: str) -> int:
    """고객사 ID로 인덱스를 찾는다. 없으면 -1을 반환한다."""
    for i, c in enumerate(customers):
        if c.get('customer_id') == customer_id:
            return i
    return -1


def create_customer(customer_id: str, customer_name: str,
                    manager_name: str, email: str) -> dict:
    """고객사를 등록한다.
    
    성공 시 {'success': True, 'data': {고객정보}}를 반환한다.
    실패 시 {'success': False, 'error': '오류메시지'}를 반환한다.
    """
    # 입력값 검증
    err = validate_customer_id(customer_id)
    if err:
        return {'success': False, 'error': err}
    err = validate_customer_name(customer_name)
    if err:
        return {'success': False, 'error': err}
    err = validate_manager_name(manager_name)
    if err:
        return {'success': False, 'error': err}
    err = validate_email(email)
    if err:
        return {'success': False, 'error': err}

    customers = load_data(CUSTOMER_FILE)

    # 중복 ID 체크
    if _find_customer(customers, customer_id) != -1:
        return {'success': False, 'error': f'이미 등록된 고객사 ID입니다: {customer_id}'}

    new_customer = {
        'customer_id': customer_id,
        'customer_name': customer_name.strip(),
        'manager_name': manager_name.strip(),
        'email': email.strip(),
    }
    customers.append(new_customer)

    if not save_data(CUSTOMER_FILE, customers):
        return {'success': False, 'error': '파일 저장 중 오류가 발생했습니다.'}

    return {'success': True, 'data': new_customer}


def list_customers() -> dict:
    """고객사 목록을 조회한다."""
    customers = load_data(CUSTOMER_FILE)
    return {'success': True, 'data': customers}


def search_customers(keyword: str) -> dict:
    """고객사명, 담당자명, 이메일에 keyword가 포함된 고객사 목록을 반환한다.
    
    대소문자를 구분하지 않으며, 빈 문자열이나 공백만 입력 시 빈 목록을 반환한다.
    """
    keyword = keyword.strip()
    if not keyword:
        return {'success': True, 'data': []}

    customers = load_data(CUSTOMER_FILE)
    keyword_lower = keyword.lower()

    matched = [
        c for c in customers
        if keyword_lower in c.get('customer_name', '').lower()
        or keyword_lower in c.get('manager_name', '').lower()
        or keyword_lower in c.get('email', '').lower()
    ]
    return {'success': True, 'data': matched}


def get_customer(customer_id: str) -> dict:
    """고객사 상세 정보를 조회한다."""
    customers = load_data(CUSTOMER_FILE)
    idx = _find_customer(customers, customer_id)
    if idx == -1:
        return {'success': False, 'error': f'고객사를 찾을 수 없습니다: {customer_id}'}
    return {'success': True, 'data': customers[idx]}


def update_customer(customer_id: str, customer_name: str,
                    manager_name: str, email: str) -> dict:
    """고객사 정보를 수정한다."""
    customers = load_data(CUSTOMER_FILE)
    idx = _find_customer(customers, customer_id)
    if idx == -1:
        return {'success': False, 'error': f'고객사를 찾을 수 없습니다: {customer_id}'}

    # 입력값 검증
    err = validate_customer_name(customer_name)
    if err:
        return {'success': False, 'error': err}
    err = validate_manager_name(manager_name)
    if err:
        return {'success': False, 'error': err}
    err = validate_email(email)
    if err:
        return {'success': False, 'error': err}

    customers[idx]['customer_name'] = customer_name.strip()
    customers[idx]['manager_name'] = manager_name.strip()
    customers[idx]['email'] = email.strip()

    if not save_data(CUSTOMER_FILE, customers):
        return {'success': False, 'error': '파일 저장 중 오류가 발생했습니다.'}

    return {'success': True, 'data': customers[idx]}


def delete_customer(customer_id: str) -> dict:
    """고객사를 삭제한다."""
    customers = load_data(CUSTOMER_FILE)
    idx = _find_customer(customers, customer_id)
    if idx == -1:
        return {'success': False, 'error': f'고객사를 찾을 수 없습니다: {customer_id}'}

    deleted = customers.pop(idx)

    if not save_data(CUSTOMER_FILE, customers):
        return {'success': False, 'error': '파일 저장 중 오류가 발생했습니다.'}

    return {'success': True, 'data': deleted}