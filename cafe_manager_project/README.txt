카페 판매 및 원재료 재고 관리 프로그램

1. 필요한 패키지 설치
   pip install PyQt5 pymysql

2. MySQL Workbench에서 schema.sql 전체 실행

3. db_helper.py에서 비밀번호 수정
   "password": "본인의 MySQL 비밀번호"

4. 실행
   python main.py

주요 기능
- 날짜별 메뉴 판매량 등록, 수정, 삭제
- 상품명 실시간 검색
- 판매량과 매출액 합계 표시
- 판매 목록 열 너비와 행 높이 정리
- 별도 원재료 재고 관리 창
- 원재료 등록, 수정, 삭제, 검색
- 최소 재고 이하 항목 경고 표시
- 주문 수량만큼 재고 자동 증가
- 주문 내역 ingredient_orders 테이블 기록
