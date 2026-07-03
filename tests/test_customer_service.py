"""고객사 관리 서비스 테스트"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch

from utils.storage import DATA_DIR
from customer_service import (
    create_customer,
    list_customers,
    get_customer,
    update_customer,
    delete_customer,
    search_customers,
)
from utils.validators import (
    validate_customer_id,
    validate_customer_name,
    validate_manager_name,
    validate_email,
)


class TestValidators(unittest.TestCase):
    """validators.py 검증 함수 테스트"""

    def test_validate_customer_id_정상(self):
        self.assertEqual(validate_customer_id('C001'), '')

    def test_validate_customer_id_빈문자열(self):
        self.assertNotEqual(validate_customer_id(''), '')

    def test_validate_customer_id_잘못된형식(self):
        self.assertNotEqual(validate_customer_id('123'), '')
        self.assertNotEqual(validate_customer_id('C01'), '')
        self.assertNotEqual(validate_customer_id('C0001'), '')

    def test_validate_customer_name_정상(self):
        self.assertEqual(validate_customer_name('테스트 고객사'), '')

    def test_validate_customer_name_빈문자열(self):
        self.assertNotEqual(validate_customer_name(''), '')

    def test_validate_customer_name_공백만(self):
        self.assertNotEqual(validate_customer_name('   '), '')

    def test_validate_manager_name_정상(self):
        self.assertEqual(validate_manager_name('홍길동'), '')

    def test_validate_manager_name_빈문자열(self):
        self.assertNotEqual(validate_manager_name(''), '')

    def test_validate_email_정상(self):
        self.assertEqual(validate_email('test@example.com'), '')

    def test_validate_email_빈문자열(self):
        self.assertNotEqual(validate_email(''), '')

    def test_validate_email_골뱅이없음(self):
        self.assertNotEqual(validate_email('testexample.com'), '')

    def test_validate_email_점없음(self):
        self.assertNotEqual(validate_email('test@example'), '')


class TestCustomerService(unittest.TestCase):
    """customer_service.py CRUD 테스트"""

    def setUp(self):
        """각 테스트 전에 임시 JSON 파일로 교체"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_data_dir = DATA_DIR
        # storage.DATA_DIR을 임시 경로로 교체
        import utils.storage
        self._orig_get_file_path = utils.storage._get_file_path
        utils.storage._get_file_path = lambda filename: os.path.join(
            self.temp_dir, f'{filename}.json'
        )
        # 빈 파일 생성
        with open(os.path.join(self.temp_dir, 'customers.json'), 'w',
                  encoding='utf-8') as f:
            json.dump([], f)

    def tearDown(self):
        """각 테스트 후 원래 경로 복원"""
        import utils.storage
        utils.storage._get_file_path = self._orig_get_file_path
        # 임시 파일 정리
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def test_등록_정상(self):
        result = create_customer('C001', '테스트 고객사', '홍길동',
                                 'hong@example.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['customer_id'], 'C001')

    def test_등록_중복ID차단(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = create_customer('C001', '또 다른 고객사', '김철수',
                                 'kim@example.com')
        self.assertFalse(result['success'])
        self.assertIn('이미 등록된', result['error'])

    def test_등록_잘못된ID형식(self):
        result = create_customer('C01', '테스트 고객사', '홍길동',
                                 'hong@example.com')
        self.assertFalse(result['success'])

    def test_등록_이메일형식오류(self):
        result = create_customer('C001', '테스트 고객사', '홍길동',
                                 'invalid-email')
        self.assertFalse(result['success'])

    def test_등록_필수값누락(self):
        result = create_customer('C001', '', '홍길동', 'hong@example.com')
        self.assertFalse(result['success'])

    def test_목록_정상(self):
        create_customer('C001', '고객사A', '홍길동', 'hong@example.com')
        create_customer('C002', '고객사B', '김철수', 'kim@example.com')
        result = list_customers()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 2)

    def test_목록_빈데이터(self):
        result = list_customers()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 0)

    def test_상세조회_정상(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = get_customer('C001')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['customer_name'], '테스트 고객사')

    def test_상세조회_존재하지않는ID(self):
        result = get_customer('C999')
        self.assertFalse(result['success'])

    def test_수정_정상(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = update_customer('C001', '수정된 고객사', '김철수',
                                 'kim@example.com')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['customer_name'], '수정된 고객사')

    def test_수정_존재하지않는ID(self):
        result = update_customer('C999', '수정된 고객사', '김철수',
                                 'kim@example.com')
        self.assertFalse(result['success'])

    def test_수정_필수값누락(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = update_customer('C001', '', '김철수', 'kim@example.com')
        self.assertFalse(result['success'])

    def test_삭제_정상(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = delete_customer('C001')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['customer_id'], 'C001')
        # 삭제 후 목록 확인
        list_result = list_customers()
        self.assertEqual(len(list_result['data']), 0)

    def test_삭제_존재하지않는ID(self):
        result = delete_customer('C999')
        self.assertFalse(result['success'])

    def test_검색_고객사명일부(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        create_customer('C002', '다른 회사', '김철수', 'kim@example.com')
        result = search_customers('테스트')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['customer_id'], 'C001')

    def test_검색_담당자명(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        create_customer('C002', '다른 회사', '김철수', 'kim@example.com')
        result = search_customers('김철수')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['customer_id'], 'C002')

    def test_검색_이메일(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = search_customers('hong')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)

    def test_검색_대소문자구분없음(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'HONG@example.com')
        result = search_customers('hong')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 1)

    def test_검색_빈문자열(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = search_customers('')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 0)

    def test_검색_공백만(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = search_customers('   ')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 0)

    def test_검색_결과없음(self):
        create_customer('C001', '테스트 고객사', '홍길동', 'hong@example.com')
        result = search_customers('존재하지않음')
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 0)


if __name__ == '__main__':
    unittest.main()