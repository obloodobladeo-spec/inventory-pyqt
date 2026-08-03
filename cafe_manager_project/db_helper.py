import pymysql


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0104",
    "database": "cafe_db",
    "charset": "utf8mb4",
}


class DB:
    def __init__(self, **config):
        self.config = config

    def _connect(self):
        return pymysql.connect(
            **self.config,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )

    def verify_user(self, username, password):
            sql = "SELECT COUNT(*) FROM users WHERE username=%s AND password=%s"
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (username, password))
                    count = cur.fetchone()['COUNT(*)']
                    print(count,)
                    return count == 1 # (True, False를 반환 해줌)

    # -------------------------
    # 메뉴
    # -------------------------
    def get_all_menus(self):
        sql = """
            SELECT menu_id, product_name, price
            FROM menus
            ORDER BY product_name
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    return cursor.fetchall()
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"메뉴 조회 실패: {error}"
            ) from error

    # -------------------------
    # 판매
    # -------------------------
    def get_sales(self, keyword=""):
        sql = """
            SELECT
                s.sale_id,
                s.sale_date,
                m.menu_id,
                m.product_name,
                m.price,
                s.sales_quantity
            FROM sales AS s
            INNER JOIN menus AS m
                ON s.menu_id = m.menu_id
        """

        params = ()

        if keyword:
            sql += " WHERE m.product_name LIKE %s"
            params = (f"%{keyword}%",)

        sql += " ORDER BY s.sale_date DESC, s.sale_id DESC"

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    return cursor.fetchall()
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"판매 내역 조회 실패: {error}"
            ) from error

    def insert_sale(self, sale_date, menu_id, sales_quantity):
        sql = """
            INSERT INTO sales (
                sale_date,
                menu_id,
                sales_quantity
            )
            VALUES (%s, %s, %s)
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            sale_date,
                            menu_id,
                            sales_quantity,
                        ),
                    )
                    connection.commit()
                    return cursor.lastrowid
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"판매 정보 등록 실패: {error}"
            ) from error

    def update_sale(
        self,
        sale_id,
        sale_date,
        menu_id,
        sales_quantity,
    ):
        sql = """
            UPDATE sales
            SET
                sale_date = %s,
                menu_id = %s,
                sales_quantity = %s
            WHERE sale_id = %s
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            sale_date,
                            menu_id,
                            sales_quantity,
                            sale_id,
                        ),
                    )
                    connection.commit()
                    return cursor.rowcount
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"판매 정보 수정 실패: {error}"
            ) from error

    def delete_sale(self, sale_id):
        sql = "DELETE FROM sales WHERE sale_id = %s"

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (sale_id,))
                    connection.commit()
                    return cursor.rowcount
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"판매 정보 삭제 실패: {error}"
            ) from error

    # -------------------------
    # 원재료
    # -------------------------
    def get_ingredients(self, keyword=""):
        sql = """
            SELECT
                ingredient_id,
                ingredient_name,
                stock,
                unit,
                minimum_stock
            FROM ingredients
        """

        params = ()

        if keyword:
            sql += " WHERE ingredient_name LIKE %s"
            params = (f"%{keyword}%",)

        sql += " ORDER BY ingredient_name"

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    return cursor.fetchall()
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"원재료 조회 실패: {error}"
            ) from error

    def insert_ingredient(
        self,
        ingredient_name,
        stock,
        unit,
        minimum_stock,
    ):
        sql = """
            INSERT INTO ingredients (
                ingredient_name,
                stock,
                unit,
                minimum_stock
            )
            VALUES (%s, %s, %s, %s)
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            ingredient_name,
                            stock,
                            unit,
                            minimum_stock,
                        ),
                    )
                    connection.commit()
                    return cursor.lastrowid
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"원재료 등록 실패: {error}"
            ) from error

    def update_ingredient(
        self,
        ingredient_id,
        ingredient_name,
        stock,
        unit,
        minimum_stock,
    ):
        sql = """
            UPDATE ingredients
            SET
                ingredient_name = %s,
                stock = %s,
                unit = %s,
                minimum_stock = %s
            WHERE ingredient_id = %s
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            ingredient_name,
                            stock,
                            unit,
                            minimum_stock,
                            ingredient_id,
                        ),
                    )
                    connection.commit()
                    return cursor.rowcount
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"원재료 수정 실패: {error}"
            ) from error

    def delete_ingredient(self, ingredient_id):
        sql = """
            DELETE FROM ingredients
            WHERE ingredient_id = %s
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (ingredient_id,))
                    connection.commit()
                    return cursor.rowcount
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"원재료 삭제 실패: {error}"
            ) from error

    def order_ingredient(self, ingredient_id, quantity):
        update_sql = """
            UPDATE ingredients
            SET stock = stock + %s
            WHERE ingredient_id = %s
        """

        order_sql = """
            INSERT INTO ingredient_orders (
                ingredient_id,
                order_quantity
            )
            VALUES (%s, %s)
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        update_sql,
                        (quantity, ingredient_id),
                    )

                    if cursor.rowcount == 0:
                        raise RuntimeError(
                            "주문할 원재료를 찾을 수 없습니다."
                        )

                    cursor.execute(
                        order_sql,
                        (ingredient_id, quantity),
                    )
                    connection.commit()

        except RuntimeError:
            raise
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"원재료 주문 실패: {error}"
            ) from error
    def get_menus_by_category(self, category):
            sql = """
                SELECT
                    menu_id,
                    product_name,
                    price,
                    category
                FROM menus
                WHERE category = %s
                ORDER BY menu_id
            """
    
            try:
                with self._connect() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(sql, (category,))
                        return cursor.fetchall()
            except pymysql.MySQLError as error:
                raise RuntimeError(
                    f"카테고리별 메뉴 조회 실패: {error}"
                ) from error
    
    def get_menu(self, menu_id):
        sql = """
            SELECT
                menu_id,
                product_name,
                price,
                category
            FROM menus
            WHERE menu_id = %s
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (menu_id,))
                    return cursor.fetchone()
        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"메뉴 조회 실패: {error}"
            ) from error
        
    def insert_menu(self, product_name, price, category):
        sql = """
            INSERT INTO menus (
                product_name,
                price,
                category
            )
            VALUES (%s, %s, %s)
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (product_name, price, category),
                    )
                    connection.commit()
                    return cursor.lastrowid

        except pymysql.err.IntegrityError as error:
            raise RuntimeError(
                "이미 등록된 메뉴명입니다."
            ) from error

        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"메뉴 등록 실패: {error}"
            ) from error

    # -------------------------
    # 메뉴 수정
    # -------------------------
    def update_menu(
        self,
        menu_id,
        product_name,
        price,
        category,
    ):
        sql = """
            UPDATE menus
            SET
                product_name = %s,
                price = %s,
                category = %s
            WHERE menu_id = %s
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            product_name,
                            price,
                            category,
                            menu_id,
                        ),
                    )
                    connection.commit()
                    return cursor.rowcount

        except pymysql.err.IntegrityError as error:
            raise RuntimeError(
                "이미 등록된 메뉴명입니다."
            ) from error

        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"메뉴 수정 실패: {error}"
            ) from error

    # -------------------------
    # 메뉴 삭제
    # -------------------------
    def delete_menu(self, menu_id):
        sql = """
            DELETE FROM menus
            WHERE menu_id = %s
        """

        try:
            with self._connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, (menu_id,))
                    connection.commit()
                    return cursor.rowcount

        except pymysql.err.IntegrityError as error:
            raise RuntimeError(
                "판매 기록에서 사용 중인 메뉴는 삭제할 수 없습니다."
            ) from error

        except pymysql.MySQLError as error:
            raise RuntimeError(
                f"메뉴 삭제 실패: {error}"
            ) from error
