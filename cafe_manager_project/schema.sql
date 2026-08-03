DROP DATABASE IF EXISTS cafe_db;

CREATE DATABASE cafe_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE cafe_db;

CREATE TABLE menus (
    menu_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL UNIQUE,
    price INT UNSIGNED NOT NULL DEFAULT 0
);

CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    sale_date DATE NOT NULL,
    menu_id INT NOT NULL,
    sales_quantity INT UNSIGNED NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sales_menu
        FOREIGN KEY (menu_id)
        REFERENCES menus(menu_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE ingredients (
    ingredient_id INT PRIMARY KEY AUTO_INCREMENT,
    ingredient_name VARCHAR(100) NOT NULL UNIQUE,
    stock DECIMAL(12, 2) UNSIGNED NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL,
    minimum_stock DECIMAL(12, 2) UNSIGNED NOT NULL DEFAULT 0
);

CREATE TABLE ingredient_orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    ingredient_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    order_quantity DECIMAL(12, 2) UNSIGNED NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT '입고완료',

    CONSTRAINT fk_orders_ingredient
        FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(ingredient_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

INSERT INTO menus (product_name, price)
VALUES
('아메리카노', 3500),
('카페라떼', 4500),
('바닐라라떼', 5000),
('카페모카', 5500),
('카라멜마끼아또', 5800),
('헤이즐넛라떼', 5300),
('콜드브루', 4500),
('콜드브루라떼', 5000),
('에스프레소', 2500),
('아인슈페너', 6000),
('초코라떼', 5300),
('딸기라떼', 5800),
('녹차라떼', 5500),
('고구마라떼', 5500),
('망고스무디', 6200),
('딸기스무디', 6200),
('블루베리스무디', 6200),
('레몬에이드', 5500),
('자몽에이드', 5500),
('청포도에이드', 5800),
('복숭아아이스티', 4000),
('캐모마일', 4500),
('페퍼민트', 4500),
('얼그레이', 4500),
('유자차', 5000),
('생강차', 5000),
('핫초코', 5000),
('쿠키앤크림프라페', 6500),
('자바칩프라페', 6800),
('민트초코프라페', 6800);

INSERT INTO sales (sale_date, menu_id, sales_quantity)
SELECT '2026-07-29', menu_id,
    CASE product_name
        WHEN '아메리카노' THEN 41
        WHEN '카페라떼' THEN 22
        WHEN '바닐라라떼' THEN 18
        WHEN '카페모카' THEN 14
        WHEN '카라멜마끼아또' THEN 12
        WHEN '헤이즐넛라떼' THEN 10
        WHEN '콜드브루' THEN 17
        WHEN '콜드브루라떼' THEN 11
        WHEN '에스프레소' THEN 8
        WHEN '아인슈페너' THEN 9
        WHEN '초코라떼' THEN 13
        WHEN '딸기라떼' THEN 15
        WHEN '녹차라떼' THEN 9
        WHEN '고구마라떼' THEN 7
        WHEN '망고스무디' THEN 8
        WHEN '딸기스무디' THEN 10
        WHEN '블루베리스무디' THEN 6
        WHEN '레몬에이드' THEN 19
        WHEN '자몽에이드' THEN 15
        WHEN '청포도에이드' THEN 12
        WHEN '복숭아아이스티' THEN 23
        WHEN '캐모마일' THEN 6
        WHEN '페퍼민트' THEN 5
        WHEN '얼그레이' THEN 8
        WHEN '유자차' THEN 4
        WHEN '생강차' THEN 3
        WHEN '핫초코' THEN 7
        WHEN '쿠키앤크림프라페' THEN 5
        WHEN '자바칩프라페' THEN 4
        WHEN '민트초코프라페' THEN 6
        ELSE 0
    END
FROM menus;

INSERT INTO ingredients (
    ingredient_name,
    stock,
    unit,
    minimum_stock
)
VALUES
('원두', 18, 'kg', 5),
('우유', 45, 'L', 15),
('바닐라 시럽', 12, 'L', 3),
('초코 소스', 9, 'kg', 3),
('카라멜 시럽', 8, 'L', 3),
('헤이즐넛 시럽', 7, 'L', 2),
('딸기 베이스', 10, 'kg', 4),
('망고 베이스', 8, 'kg', 3),
('블루베리 베이스', 4, 'kg', 4),
('레몬청', 6, 'kg', 2),
('자몽청', 5, 'kg', 2),
('청포도 베이스', 5, 'kg', 2),
('녹차 파우더', 6, 'kg', 2),
('고구마 파우더', 4, 'kg', 2),
('휘핑크림', 15, 'L', 5),
('얼음', 120, 'kg', 30),
('테이크아웃 컵', 800, '개', 250),
('컵 뚜껑', 760, '개', 250),
('빨대', 180, '개', 200),
('냅킨', 900, '개', 300);
