"""영업일지 관리 서비스 테스트"""

import os
import json
import tempfile
import unittest

from utils.storage import DATA_DIR
from utils.validators import (
    validate_date,
    validate_content,
    validate_report_id,
)
from sales_report_service import (
    create_report,
    list_reports,
    get_report,
    update_report,
    validate_customer_id_for_report,
)


class TestValidators(unittest.TestCase):
    """validators.py 영업일지 관련 검증 함수 테스트"""

    def test_validate_date_정상(self):
        self.assertEqual(validate_date('2026-07-03'), '')

    def test_validate_date_빈문자열(self):
        self.assertNotEqual(validate_date(''), '')

    def test_validate_date_잘못된형식(self):
        self.assertNotEqual(validate_date('2026/07/03'), '')
        self.assertNotEqual(validate_date('2026-7-3'), '')
        self.assertNotEqual(validate_date('07-03-2026'), '')

    def test_validate_date_존재하지않는날짜(self):
        self.assertNotEqual(validate_date('2026-13-01'), '')
        self.assertNotEqual(validate_date('2026-02-30'), '')

    def test_validate_content_정상(self):
        self.assertEqual(validate_content('방문 상담 진행'), '')

    def test_validate_content_빈문자열(self):
        self.assertNotEqual(validate_content(''), '')

    def test_validate_content_공백만(self):
        self.assertNotEqual(validate_content('   '), '')

    def test_validate_report_id_정상(self):
        self.assertEqual(validate_report_id('R001'), '')

    def test_validate_report_id_빈문자열(self):
        self.assertNotEqual(validate_report_id(''), '')

    def test_validate_report_id_잘못된형식(self):
        self.assertNotEqual(validate_report_id('R01'), '')
        self.assertNotEqual(validate_report_id('R0001'), '')
        self.assertNotEqual(validate_report_id('001'), '')
        self.assertNotEqual(validate_report_id('ABC'), '')


class TestSalesReportService(unittest.TestCase):
    """sales_report_service.py CRUD 테스트"""

    def setUp(self):
        """각 테스트 전에 임시 JSON 파일로 교체"""
        self.temp_dir = tempfile.mkdtemp()
        # storage._get_file_path를 임시 경로로 교체
        import utils.storage
        self._orig_get_file_path = utils.storage._get_file_path
        utils.storage._get_file_path = lambda filename: os.path.join(
            self.temp_dir, f'{filename}.json'
        )
        # customers.json 초기 데이터 (테스트용 고객사)
        with open(os.path.join(self.temp_dir, 'customers.json'), 'w',
                  encoding='utf-8') as f:
            json.dump([
                {'customer_id': 'C001', 'customer_name': '테스트 고객사',
                 'manager_name': '홍길동', 'email': 'hong@example.com'}
            ], f)
        # sales_reports.json 빈 파일 생성
        with open(os.path.join(self.temp_dir, 'sales_reports.json'), 'w',
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

    # ---------- 영업일지 등록 테스트 ----------

    def test_등록_정상(self):
        result = create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['report_id'], 'R001')
        self.assertEqual(result['data']['status'], 'DRAFT')

    def test_등록_중복ID차단(self):
        create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        result = create_report('R001', 'C001', '2026-07-04', '추가 상담')
        self.assertFalse(result['success'])
        self.assertIn('이미 등록된', result['error'])

    def test_등록_존재하지않는고객사(self):
        result = create_report('R001', 'C999', '2026-07-03', '방문 상담 진행')
        self.assertFalse(result['success'])
        self.assertIn('존재하지 않는 고객사', result['error'])

    def test_등록_잘못된ID형식(self):
        result = create_report('R01', 'C001', '2026-07-03', '방문 상담 진행')
        self.assertFalse(result['success'])

    def test_등록_고객사ID누락(self):
        result = create_report('R001', '', '2026-07-03', '방문 상담 진행')
        self.assertFalse(result['success'])

    def test_등록_날짜형식오류(self):
        result = create_report('R001', 'C001', '2026/07/03', '방문 상담 진행')
        self.assertFalse(result['success'])

    def test_등록_존재하지않는날짜(self):
        result = create_report('R001', 'C001', '2026-02-30', '방문 상담 진행')
        self.assertFalse(result['success'])

    def test_등록_내용누락(self):
        result = create_report('R001', 'C001', '2026-07-03', '')
        self.assertFalse(result['success'])

    def test_등록_내용공백만(self):
        result = create_report('R001', 'C001', '2026-07-03', '   ')
        self.assertFalse(result['success'])

    # ---------- 영업일지 목록 조회 테스트 ----------

    def test_목록_정상(self):
        create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        create_report('R002', 'C001', '2026-07-04', '전화 통화')
        result = list_reports()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 2)

    def test_목록_빈데이터(self):
        result = list_reports()
        self.assertTrue(result['success'])
        self.assertEqual(len(result['data']), 0)

    # ---------- 영업일지 상세 조회 테스트 ----------

    def test_상세조회_정상(self):
        create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        result = get_report('R001')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['content'], '방문 상담 진행')

    def test_상세조회_존재하지않는ID(self):
        result = get_report('R999')
        self.assertFalse(result['success'])

    # ---------- 영업일지 수정 테스트 ----------

    def test_수정_정상(self):
        create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        result = update_report('R001', '2026-07-04', '수정된 내용')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['date'], '2026-07-04')
        self.assertEqual(result['data']['content'], '수정된 내용')

    def test_수정_존재하지않는ID(self):
        result = update_report('R999', '2026-07-04', '수정된 내용')
        self.assertFalse(result['success'])

    def test_수정_날짜형식오류(self):
        create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        result = update_report('R001', '2026/07/04', '수정된 내용')
        self.assertFalse(result['success'])

    def test_수정_내용누락(self):
        create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        result = update_report('R001', '2026-07-04', '')
        self.assertFalse(result['success'])

    # ---------- APPROVED 상태 차단 테스트 ----------

    def test_수정_APPROVED상태차단(self):
        """APPROVED 상태의 영업일지는 수정할 수 없다."""
        create_report('R001', 'C001', '2026-07-03', '방문 상담 진행')
        # 상태를 APPROVED로 변경 (실제 저장 데이터 직접 수정)
        filepath = os.path.join(self.temp_dir, 'sales_reports.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        for r in reports:
            if r['report_id'] == 'R001':
                r['status'] = 'APPROVED'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        # 수정 시도 → 차단
        result = update_report('R001', '2026-07-04', '수정된 내용')
        self.assertFalse(result['success'])
        self.assertIn('승인된', result['error'])


if __name__ == '__main__':
    unittest.main()