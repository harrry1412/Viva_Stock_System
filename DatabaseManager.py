import configparser
from datetime import datetime
import mysql.connector
from mysql.connector import pooling


class DatabaseManager:
    '''
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('mysql.txt')
        self.host = config.get('database', 'host')
        self.user = config.get('database', 'user')
        self.password = config.get('database', 'password')
        self.database = config.get('database', 'database')

    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
    '''
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
        self.pool_size = 1  # 这是连接池中连接的数量
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

    def fetch_rugs(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, qty, supplier, note, image FROM rug order by supplier, sort, id ASC")
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
        query = f"SELECT id, qty, supplier, note, image FROM rug ORDER BY {key} {direction}"
        cursor.execute(query)  # 不需要传递参数了
        rows = cursor.fetchall()
        conn.close()
        return rows


    
    def fetch_records(self, id):
        conn = self.connect()
        cursor = conn.cursor()
        query="SELECT id, dat, usr, content FROM record WHERE id=%s order by dat DESC"
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

    def insert_record(self, record_id, user, content, date):
        conn = self.connect()
        cursor = conn.cursor()
        insert_query = "INSERT INTO record (id, dat, usr, content) value (%s, %s, %s, %s)"
        cursor.execute(insert_query, (record_id, date, user, content))
        conn.commit()
        conn.close()

    '''
    def insert_product(self, product_data):
        try:
            conn = self.connect()
            cursor = conn.cursor()
            insert_query = "INSERT INTO rug (qty, supplier, note, image, id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, product_data)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error inserting product: {err}")
    '''        
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

