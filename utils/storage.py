import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def _get_file_path(filename: str) -> str:
    """data 디렉터리의 JSON 파일 경로를 반환한다."""
    return os.path.join(DATA_DIR, f'{filename}.json')


def load_data(filename: str) -> list:
    """JSON 파일을 읽어 리스트로 반환한다.
    
    파일이 없거나 잘못된 JSON 형식이면 빈 리스트를 반환한다.
    """
    filepath = _get_file_path(filename)
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
    except (json.JSONDecodeError, IOError):
        return []


def save_data(filename: str, data: list) -> bool:
    """리스트를 JSON 파일로 저장한다.
    
    성공 시 True, 실패 시 False를 반환한다.
    """
    if not isinstance(data, list):
        return False
    filepath = _get_file_path(filename)
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False