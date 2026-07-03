"""영업일지 결재 서비스 테스트"""

import os
import json
import tempfile
import unittest

from approval_service import (
    submit_report,
    approve_report,
    reject_report,
    withdraw_report,
)


class TestApprovalService(unittest.TestCase):
    """approval_service.py 상태 전이 테스트"""

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
        # sales_reports.json 초기 데이터 생성
        self._init_reports()

    def tearDown(self):
        """각 테스트 후 원래 경로 복원"""
        import utils.storage
        utils.storage._get_file_path = self._orig_get_file_path
        # 임시 파일 정리
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        os.rmdir(self.temp_dir)

    def _init_reports(self):
        """기본 테스트용 영업일지 3건을 생성한다."""
        reports = [
            {'report_id': 'R001', 'customer_id': 'C001',
             'date': '2026-07-01', 'content': 'DRAFT 상태 보고서',
             'status': 'DRAFT'},
            {'report_id': 'R002', 'customer_id': 'C001',
             'date': '2026-07-02', 'content': 'SUBMITTED 상태 보고서',
             'status': 'SUBMITTED'},
            {'report_id': 'R003', 'customer_id': 'C001',
             'date': '2026-07-03', 'content': 'APPROVED 상태 보고서',
             'status': 'APPROVED'},
            {'report_id': 'R004', 'customer_id': 'C001',
             'date': '2026-07-04', 'content': 'REJECTED 상태 보고서',
             'status': 'REJECTED'},
        ]
        filepath = os.path.join(self.temp_dir, 'sales_reports.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)

    def _get_status(self, report_id: str) -> str:
        """지정한 보고서의 현재 상태를 반환한다."""
        filepath = os.path.join(self.temp_dir, 'sales_reports.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        for r in reports:
            if r['report_id'] == report_id:
                return r['status']
        return ''

    # ---------- 정상 전이 테스트 ----------

    def test_submit_DRAFT_to_SUBMITTED(self):
        """DRAFT → submit → SUBMITTED"""
        result = submit_report('R001')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['status'], 'SUBMITTED')
        self.assertEqual(self._get_status('R001'), 'SUBMITTED')

    def test_approve_SUBMITTED_to_APPROVED(self):
        """SUBMITTED → approve → APPROVED"""
        result = approve_report('R002')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['status'], 'APPROVED')
        self.assertEqual(self._get_status('R002'), 'APPROVED')

    def test_reject_SUBMITTED_to_REJECTED(self):
        """SUBMITTED → reject → REJECTED"""
        result = reject_report('R002')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['status'], 'REJECTED')
        self.assertEqual(self._get_status('R002'), 'REJECTED')

    def test_withdraw_SUBMITTED_to_DRAFT(self):
        """SUBMITTED → withdraw → DRAFT"""
        result = withdraw_report('R002')
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['status'], 'DRAFT')
        self.assertEqual(self._get_status('R002'), 'DRAFT')

    # ---------- DRAFT 상태에서 잘못된 전이 차단 ----------

    def test_DRAFT_approve_차단(self):
        """DRAFT 상태에서 approve는 허용되지 않음"""
        result = approve_report('R001')
        self.assertFalse(result['success'])
        self.assertIn('허용되지 않습니다', result['error'])
        self.assertEqual(self._get_status('R001'), 'DRAFT')

    def test_DRAFT_reject_차단(self):
        """DRAFT 상태에서 reject는 허용되지 않음"""
        result = reject_report('R001')
        self.assertFalse(result['success'])
        self.assertIn('허용되지 않습니다', result['error'])
        self.assertEqual(self._get_status('R001'), 'DRAFT')

    def test_DRAFT_withdraw_차단(self):
        """DRAFT 상태에서 withdraw는 허용되지 않음"""
        result = withdraw_report('R001')
        self.assertFalse(result['success'])
        self.assertIn('허용되지 않습니다', result['error'])
        self.assertEqual(self._get_status('R001'), 'DRAFT')

    # ---------- SUBMITTED 상태에서 잘못된 전이 차단 ----------

    def test_SUBMITTED_submit_차단(self):
        """SUBMITTED 상태에서 submit(중복 제출)은 허용되지 않음"""
        result = submit_report('R002')
        self.assertFalse(result['success'])
        self.assertIn('허용되지 않습니다', result['error'])
        self.assertEqual(self._get_status('R002'), 'SUBMITTED')

    # ---------- APPROVED 상태에서 모든 전이 차단 ----------

    def test_APPROVED_submit_차단(self):
        """APPROVED 상태에서 submit은 허용되지 않음"""
        result = submit_report('R003')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R003'), 'APPROVED')

    def test_APPROVED_approve_차단(self):
        """APPROVED 상태에서 approve는 허용되지 않음"""
        result = approve_report('R003')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R003'), 'APPROVED')

    def test_APPROVED_reject_차단(self):
        """APPROVED 상태에서 reject는 허용되지 않음"""
        result = reject_report('R003')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R003'), 'APPROVED')

    def test_APPROVED_withdraw_차단(self):
        """APPROVED 상태에서 withdraw는 허용되지 않음"""
        result = withdraw_report('R003')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R003'), 'APPROVED')

    # ---------- REJECTED 상태에서 모든 전이 차단 ----------

    def test_REJECTED_submit_차단(self):
        """REJECTED 상태에서 submit은 허용되지 않음"""
        result = submit_report('R004')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R004'), 'REJECTED')

    def test_REJECTED_approve_차단(self):
        """REJECTED 상태에서 approve는 허용되지 않음"""
        result = approve_report('R004')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R004'), 'REJECTED')

    def test_REJECTED_reject_차단(self):
        """REJECTED 상태에서 reject는 허용되지 않음"""
        result = reject_report('R004')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R004'), 'REJECTED')

    def test_REJECTED_withdraw_차단(self):
        """REJECTED 상태에서 withdraw는 허용되지 않음"""
        result = withdraw_report('R004')
        self.assertFalse(result['success'])
        self.assertIn('결재 작업을 수행할 수 없습니다', result['error'])
        self.assertEqual(self._get_status('R004'), 'REJECTED')

    # ---------- 존재하지 않는 보고서 ----------

    def test_존재하지않는보고서_submit(self):
        result = submit_report('R999')
        self.assertFalse(result['success'])
        self.assertIn('찾을 수 없습니다', result['error'])

    def test_존재하지않는보고서_approve(self):
        result = approve_report('R999')
        self.assertFalse(result['success'])
        self.assertIn('찾을 수 없습니다', result['error'])

    def test_존재하지않는보고서_reject(self):
        result = reject_report('R999')
        self.assertFalse(result['success'])
        self.assertIn('찾을 수 없습니다', result['error'])

    def test_존재하지않는보고서_withdraw(self):
        result = withdraw_report('R999')
        self.assertFalse(result['success'])
        self.assertIn('찾을 수 없습니다', result['error'])


if __name__ == '__main__':
    unittest.main()