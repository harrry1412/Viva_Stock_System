import configparser
from datetime import datetime
import mysql.connector
from mysql.connector import pooling


class DatabaseManager:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('mysql.txt')
        self.database_config = {
            'host': config.get('database', 'host'),
            'user': config.get('database', 'user'),
            'password': config.get('database', 'password'),
            'database': config.get('database', 'database')
        }
        self.pool_name = 'mypool'
        self.pool_size = 5  # 这是连接池中连接的数量
        self.pool = pooling.MySQLConnectionPool(pool_name=self.pool_name,
                                                pool_size=self.pool_size,
                                                **self.database_config)

    def connect(self):
        return self.pool.get_connection()
    
    def fetch_supplier(self):
        conn=self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT supplier FROM rug")
        suppliers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return suppliers
    
    def fetch_category(self):
        conn=self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM rug")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def fetch_rugs(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, qty, supplier, category, note, image FROM rug order by supplier, sort, id ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def fetch_ordered_rugs(self, key, direction):
        # 首先验证 key 是一个有效的列名
        valid_keys = ['id', 'qty', 'supplier', 'note', 'image']
        if key not in valid_keys:
            raise ValueError("Invalid order key")

        # 同样，验证 direction 是一个有效的排序方向
        valid_directions = ['ASC', 'DESC']
        if direction not in valid_directions:
            raise ValueError("Invalid order direction")

        conn = self.connect()
        cursor = conn.cursor()

        # 包括排序方向参数
        query = f"SELECT id, qty, supplier, category, note, image FROM rug ORDER BY {key} {direction}"
        cursor.execute(query)  # 不需要传递参数了
        rows = cursor.fetchall()
        conn.close()
        return rows


    
    def fetch_records(self, id):
        conn = self.connect()
        cursor = conn.cursor()
        query="SELECT id, dat, usr, content, bef, aft FROM record WHERE id=%s order by dat DESC"
        cursor.execute(query, (id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def fetch_userPwd(self, username):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT pwd FROM user WHERE name=%s"
        try:
            cursor.execute(query, (username,))
            rows = cursor.fetchall()
            if rows:
                # 获取第一个匹配项的密码
                return rows[0][0]
        except Exception as e:
            print(f"Error fetching password: {e}")
        finally:
            conn.close()
        return None

    def update_rug_quantity(self, rug_id, new_quantity):
        conn = self.connect()
        cursor = conn.cursor()
        update_query = "UPDATE rug SET qty = %s WHERE id = %s"
        cursor.execute(update_query, (new_quantity, rug_id))
        conn.commit()
        conn.close()

    def insert_record(self, record_id, user, content, bef, aft, date):
        conn = self.connect()
        cursor = conn.cursor()
        # 请确保下面的SQL语句中的列名与您数据库中的列名相匹配
        insert_query = """
        INSERT INTO record (id, usr, content, bef, aft, dat) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        # 执行插入操作
        cursor.execute(insert_query, (record_id, user, content, bef, aft, date))
        # 提交更改
        conn.commit()
        # 关闭连接
        cursor.close()
        conn.close()

  
    def insert_product(self, product_data):
        for data in product_data:
            if(data is None):
                data=''
        try:
            conn = self.connect()
            cursor = conn.cursor()
            insert_query = "INSERT INTO rug (id, qty, supplier, note, image) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, product_data)  # Directly pass the product_data tuple
            conn.commit()
            return True  # Return True to indicate success
        except mysql.connector.Error as err:
            print(f"Error inserting product: {err}")
            return False  # Return False to indicate failure
        finally:
            if conn.is_connected():
                conn.close()

    def id_exists(self, id):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT count(*) FROM rug WHERE id=%s"
        
        try:
            cursor.execute(query, (id,))
            (count,) = cursor.fetchone()
            return count > 0
        except Exception as e:
            print(f"Error checking id existence: {e}")
            return False
        finally:
            conn.close()

    def fetch_records_for_rug(self, id):
        conn = self.connect()
        cursor = conn.cursor()

        # 编写 SQL 查询，用于获取与特定 rug_id 相关联的记录
        query = "SELECT dat, content, bef, aft FROM record WHERE id = %s ORDER BY dat DESC"
        cursor.execute(query, (id,))

        # 获取查询结果
        records = cursor.fetchall()

        conn.close()
        return records

