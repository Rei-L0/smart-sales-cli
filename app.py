"""Smart Sales CLI - 메인 메뉴"""

from customer_service import (
    create_customer,
    list_customers,
    get_customer,
    update_customer,
    delete_customer,
    search_customers,
)


def print_menu():
    """메인 메뉴를 출력한다."""
    print('\n' + '=' * 40)
    print('         Smart Sales CLI')
    print('=' * 40)
    print(' 1. 고객사 관리')
    print(' 2. 영업일지 관리')
    print(' 3. 결재 관리')
    print(' 4. 활동 요약')
    print(' 0. 종료')
    print('=' * 40)


def print_customer_menu():
    """고객사 관리 서브메뉴를 출력한다."""
    print('\n' + '-' * 40)
    print('       고객사 관리')
    print('-' * 40)
    print(' 1. 고객사 등록')
    print(' 2. 고객사 목록')
    print(' 3. 고객사 상세 조회')
    print(' 4. 고객사 수정')
    print(' 5. 고객사 삭제')
    print(' 6. 고객사 검색')
    print(' 0. 돌아가기')
    print('-' * 40)


def run_customer_menu():
    """고객사 관리 서브메뉴를 실행한다."""
    while True:
        print_customer_menu()
        choice = input('선택: ').strip()

        if choice == '0':
            break
        elif choice == '1':
            customer_id = input('고객사 ID: ').strip()
            customer_name = input('고객사명: ').strip()
            manager_name = input('담당자명: ').strip()
            email = input('이메일: ').strip()
            result = create_customer(customer_id, customer_name,
                                     manager_name, email)
            if result['success']:
                print(f'등록 완료: {result["data"]["customer_name"]}')
            else:
                print(f'오류: {result["error"]}')
        elif choice == '2':
            result = list_customers()
            if result['success']:
                customers = result['data']
                if not customers:
                    print('등록된 고객사가 없습니다.')
                else:
                    print(f'\n전체 고객사 ({len(customers)}건)')
                    for c in customers:
                        print(f'  {c["customer_id"]} | {c["customer_name"]} | '
                              f'{c["manager_name"]} | {c["email"]}')
            else:
                print(f'오류: {result["error"]}')
        elif choice == '3':
            customer_id = input('고객사 ID: ').strip()
            result = get_customer(customer_id)
            if result['success']:
                c = result['data']
                print(f'\n고객사 ID: {c["customer_id"]}')
                print(f'고객사명: {c["customer_name"]}')
                print(f'담당자명: {c["manager_name"]}')
                print(f'이메일: {c["email"]}')
            else:
                print(f'오류: {result["error"]}')
        elif choice == '4':
            customer_id = input('고객사 ID: ').strip()
            customer_name = input('새 고객사명: ').strip()
            manager_name = input('새 담당자명: ').strip()
            email = input('새 이메일: ').strip()
            result = update_customer(customer_id, customer_name,
                                     manager_name, email)
            if result['success']:
                print(f'수정 완료: {result["data"]["customer_name"]}')
            else:
                print(f'오류: {result["error"]}')
        elif choice == '5':
            customer_id = input('고객사 ID: ').strip()
            result = delete_customer(customer_id)
            if result['success']:
                print(f'삭제 완료: {result["data"]["customer_name"]}')
            else:
                print(f'오류: {result["error"]}')
        elif choice == '6':
            keyword = input('검색어: ').strip()
            result = search_customers(keyword)
            if result['success']:
                customers = result['data']
                if not customers:
                    print('검색 결과가 없습니다.')
                else:
                    print(f'\n검색 결과 ({len(customers)}건)')
                    for c in customers:
                        print(f'  {c["customer_id"]} | {c["customer_name"]} | '
                              f'{c["manager_name"]} | {c["email"]}')
            else:
                print(f'오류: {result["error"]}')
        else:
            print('잘못된 선택입니다.')


def main():
    """CLI 메인 진입점"""
    print('Smart Sales CLI를 시작합니다.')
    
    while True:
        print_menu()
        choice = input('선택: ').strip()
        
        if choice == '0':
            print('프로그램을 종료합니다.')
            break
        elif choice == '1':
            run_customer_menu()
        else:
            print(f'선택한 메뉴: {choice} (아직 구현되지 않음)')


if __name__ == '__main__':
    main()
