import configparser
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
    
    def fetch_rug_by_id(self, rug_id):
        conn = self.connect()
        try:
            cursor = conn.cursor(dictionary=True)  # 使用字典格式的游标
            query = "SELECT * FROM rug WHERE id = %s"
            cursor.execute(query, (rug_id,))
            rug_data = cursor.fetchall()
            if rug_data:
                return rug_data[0]  # 返回第一条记录作为字典
        except Exception as e:
            print(f"Error fetching rug data: {e}")
        finally:
            if conn.is_connected():
                conn.close()
        return None
    
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

    def insert_record(self, record_id, user, content, bef, aft, date, edit_date):
        conn = self.connect()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO record (id, usr, content, bef, aft, dat, editdate) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        # 执行插入操作
        cursor.execute(insert_query, (record_id, user, content, bef, aft, date, edit_date))
        # 提交更改
        conn.commit()
        # 关闭连接
        cursor.close()
        conn.close()

    def insert_note_record(self, record_id, user, bef, aft, date):
        conn = self.connect()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO note_record (id, usr, bef, aft, dat) 
        VALUES (%s, %s, %s, %s, %s)
        """
        # 执行插入操作
        cursor.execute(insert_query, (record_id, user, bef, aft, date))
        # 提交更改
        conn.commit()
        # 关闭连接
        cursor.close()
        conn.close()

    def insert_edit_product_record(self, user, old, new, date):
        conn = self.connect()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO edit_product_record (usr, old_info, new_info, editdate) 
        VALUES (%s, %s, %s, %s)
        """
        # 执行插入操作
        cursor.execute(insert_query, (user, old, new, date))
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
            insert_query = "INSERT INTO rug (id, qty, category, supplier, note, image, adddate, adduser) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
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

        query = "SELECT dat, content, bef, aft FROM record WHERE id = %s AND deleted=0 ORDER BY editdate DESC"
        cursor.execute(query, (id,))

        # 获取查询结果
        records = cursor.fetchall()

        conn.close()
        return records
    
    def fetch_records(self, id):
        conn = self.connect()
        cursor = conn.cursor()
        query="SELECT id, dat, usr, content, bef, aft, editdate, deleted FROM record WHERE id=%s AND deleted=0 order by editdate DESC"
        cursor.execute(query, (id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_note(self, note, rug_id):
        conn = self.connect()
        cursor = conn.cursor()
        update_query="UPDATE rug SET note = %s WHERE id = %s"
        cursor.execute(update_query, (note, rug_id))
        conn.commit()
        conn.close()


    def update_rug_info(self, old_model_id, new_rug_data):
        conn = self.connect()
        cursor = conn.cursor()
        update_query = """
        UPDATE rug
        SET id = %s, supplier = %s, category = %s, image = %s
        WHERE id = %s
        """
        try:
            # 执行更新操作
            cursor.execute(update_query, (
                new_rug_data['model'],
                new_rug_data['supplier'],
                new_rug_data['category'],
                new_rug_data['image'],
                old_model_id
            ))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error updating rug: {err}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def check_user_permission(self, user, permission):
        conn = self.connect()
        cursor = conn.cursor()
        query = "SELECT count(*) FROM user_permission WHERE usr=%s and permission=%s"
        
        try:
            cursor.execute(query, (user, permission))
            (count,) = cursor.fetchone()
            return count > 0
        except Exception as e:
            print(f"Error checking user permission: {e}")
            return False
        finally:
            conn.close()

    def delete_record(self, id, user, date, now):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
        UPDATE record
        SET del_user = %s, 
            del_date = %s,
            deleted = 1
        WHERE id=%s AND editdate = %s;
        """
        
        try:
            # 执行更新操作
            cursor.execute(query, (user, now, id, date))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating record: {e}")
            conn.rollback()  # 如果出现异常，回滚更改
            return False
        finally:
            conn.close()

    def fetch_record_bef(self, id, date):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
        SELECT bef FROM record
        WHERE id=%s AND editdate=%s;
        """
        
        try:
            # 执行查询操作
            cursor.execute(query, (id, date))
            result = cursor.fetchone()  # 获取查询结果
            if result:
                return result[0]  # 返回查询到的bef值
            else:
                return None  # 如果没有查询到结果，返回None
        except Exception as e:
            print(f"Error fetching record bef: {e}")
            return None  # 如果出现异常，返回None
        finally:
            conn.close()  # 关闭数据库连接

    def fetch_qty(self, id):
        conn = self.connect()
        cursor = conn.cursor()
        query = """
        SELECT qty FROM rug
        WHERE id=%s;
        """
        
        try:
            # 执行查询操作
            cursor.execute(query, (id,))
            result = cursor.fetchone() 
            if result:
                return result[0] 
            else:
                return None  # 如果没有查询到结果，返回None
        except Exception as e:
            print(f"Error fetching qty: {e}")
            return None  # 如果出现异常，返回None
        finally:
            conn.close()  # 关闭数据库连接




