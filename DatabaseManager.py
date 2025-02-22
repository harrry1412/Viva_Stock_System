import configparser
import mysql.connector
from mysql.connector import pooling, Error
import datetime

import os
import sys
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class DatabaseManager:
    def __init__(self):
        # 默认配置文件路径
        config_path = 'mysql.txt'
        # 尝试连接
        self.initialized=False
        if not self.try_connect(config_path):
            # 如果第一次连接失败，尝试备用路径
            backup_config_path = '\\\\VIVA303-WORK\\Viva店面共享\\StockImg\\mysql.txt'
            if not self.try_connect(backup_config_path):
                # 如果备用路径也失败，打印错误信息
                print("Both attempts to connect to the database have failed.")

    def try_connect(self, config_path):
        if not os.path.exists(config_path):
            print(f"Configuration file {config_path} not found.")
            self.exit_with_conn_error()
            return False

        config = configparser.ConfigParser()
        config.read(config_path)
        
        database_config = {
            'host': config.get('database', 'host'),
            'user': config.get('database', 'user'),
            'password': config.get('database', 'password'),
            'database': config.get('database', 'database')
        }
        pool_name = 'mypool'
        pool_size = 5  # 这是连接池中连接的数量

        try:
            pool = pooling.MySQLConnectionPool(pool_name=pool_name,
                                               pool_size=pool_size,
                                               **database_config)
            self.pool = pool
            self.initialized = True
            return True
        except Error as e:
            print(f"Error creating connection pool from {config_path}: {e}")
            return False

    def connect(self):
        if not self.initialized:
            print("Connection pool is not initialized.")
            return None
        try:
            return self.pool.get_connection()
        except Error as e:
            print(f"Error connecting to the database: {e}")
            return None
    
    def fetch_supplier(self):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT supplier FROM rug where deleted=0")
            suppliers = [row[0] for row in cursor.fetchall()]
            return suppliers
        except Exception as e:
            print(f"Error fetching suppliers: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def fetch_category(self):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM rug where deleted=0")
            categories = [row[0] for row in cursor.fetchall()]
            return categories
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def fetch_rugs(self):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, qty, supplier, category, note, image FROM rug where deleted=0 ORDER BY supplier, sort, id ASC")
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching rugs: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def fetch_rug_by_id(self, rug_id):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)  # 使用字典格式的游标
            query = "SELECT * FROM rug WHERE id = %s and deleted=0"
            cursor.execute(query, (rug_id,))
            rug_data = cursor.fetchall()
            if rug_data:
                return rug_data[0]  # 如果查询到数据，返回第一条记录作为字典
        except Exception as e:
            print(f"查询rug数据时出错: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def fetch_ordered_rugs(self, key, direction):
        # 验证 key 是否为有效的列名
        valid_keys = ['id', 'qty', 'supplier', 'note', 'image']
        if key not in valid_keys:
            raise ValueError("无效的排序键")

        # 验证 direction 是否为有效的排序方向
        valid_directions = ['ASC', 'DESC']
        if direction not in valid_directions:
            raise ValueError("无效的排序方向")

        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            # 构建包含排序方向参数的查询
            query = f"SELECT id, qty, supplier, category, note, image FROM rug where deleted=0 ORDER BY {key} {direction}"
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(f"查询有序rugs时出错: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    
    def fetch_userPwd_status(self, username):
        conn = None
        try:
            conn = self.connect()
            if conn:
                cursor = conn.cursor()
            else:
                return -1
            query = "SELECT pwd, status FROM user WHERE name=%s"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                # 构建并返回包含密码和状态的字典
                return {'password': row[0], 'status': row[1]}
        except Exception as e:
            print(f"获取用户密码和状态时出错: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_rug_quantity(self, rug_id, new_quantity):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            update_query = "UPDATE rug SET qty = %s WHERE id = %s and deleted=0"
            cursor.execute(update_query, (new_quantity, rug_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"更新rug数量时出错: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def insert_record(self, record_id, user, content, bef, aft, date, edit_date):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO record (id, usr, content, bef, aft, dat, editdate) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (record_id, user, content, bef, aft, date, edit_date))
            conn.commit()
            # 更新最后修改时间
            self.update_last_modified_time(user)
            return True
        except Exception as e:
            print(f"插入记录时发生错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def insert_note_record(self, record_id, user, bef, aft, date):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO note_record (id, usr, bef, aft, dat) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (record_id, user, bef, aft, date))
            conn.commit()
            # 更新最后修改时间
            self.update_last_modified_time(user)
            return True
        except Exception as e:
            print(f"插入笔记记录时发生错误: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def insert_edit_product_record(self, user, old, new, date):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO edit_product_record (usr, old_info, new_info, editdate) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (user, old, new, date))
            conn.commit()
            self.update_last_modified_time(user) # 更新最后修改时间
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()


    def insert_product(self, product_data):
        # 处理数据中的None值
        processed_data = []
        for data in product_data:
            if data is None:
                processed_data.append('')
            else:
                processed_data.append(data)
        processed_data = tuple(processed_data)  # 转换为元组以符合cursor.execute的要求

        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            insert_query = "INSERT INTO rug (id, qty, category, supplier, note, image, adddate, adduser) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, processed_data)
            conn.commit()
            self.update_last_modified_time(processed_data[7])  # 更新最后修改时间
            return True
        except Exception as e:
            print(f"插入产品时出错: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()


    def id_exists(self, id):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = "SELECT count(*) FROM rug WHERE id=%s and deleted=0"
            
            cursor.execute(query, (id,))
            (count,) = cursor.fetchone()
            
            return count > 0
        except Exception as e:
            print(f"Error checking id existence: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def supplier_exists(self, sup):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # 先查询是否存在完全匹配的 supplier（大小写敏感）
            exact_match_query = "SELECT supplier FROM rug WHERE BINARY supplier = %s AND deleted = 0 LIMIT 1"
            cursor.execute(exact_match_query, (sup,))
            exact_match = cursor.fetchone()

            if exact_match:
                return True  # 大小写完全匹配，返回 True

            # 如果没有完全匹配，再查询是否有大小写不同但忽略大小写相同的 supplier
            case_insensitive_query = "SELECT supplier FROM rug WHERE LOWER(supplier) = LOWER(%s) AND deleted = 0 LIMIT 1"
            cursor.execute(case_insensitive_query, (sup,))
            case_insensitive_match = cursor.fetchone()

            if case_insensitive_match:
                return case_insensitive_match[0]  # 返回数据库中的原始 supplier

            return False  # 没有匹配项
        except Exception as e:
            print(f"Error checking Supplier existence: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()



    def fetch_records_for_rug(self, id):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = "SELECT dat, content, bef, aft FROM record WHERE id = %s AND deleted=0 ORDER BY editdate DESC"
            cursor.execute(query, (id,))
            records = cursor.fetchall()
            return records
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def fetch_records(self, id):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = "SELECT id, dat, usr, content, bef, aft, editdate, deleted FROM record WHERE id=%s AND deleted=0 ORDER BY editdate DESC"
            cursor.execute(query, (id,))
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_record_ids(self, old_id, new_id):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            update_query = """
            UPDATE record
            SET id = %s
            WHERE id = %s AND deleted = 0
            """
            # 执行更新操作
            cursor.execute(update_query, (new_id, old_id))
            conn.commit()
            # 返回更新的行数，可以提供反馈信息
            rows_updated = cursor.rowcount
            print(f"{rows_updated} records updated.")
            return True
        except Exception as e:
            print(f"An error occurred while updating record ids: {e}")
            if conn:
                conn.rollback()  # 事务回滚
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()


    def update_note(self, note, rug_id):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            update_query = "UPDATE rug SET note = %s WHERE id = %s and deleted=0"
            cursor.execute(update_query, (note, rug_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"An error occurred while updating the note: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()


    def update_rug_info(self, old_model_id, new_rug_data):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            update_query = """
            UPDATE rug
            SET id = %s, supplier = %s, category = %s, image = %s
            WHERE id = %s and deleted=0
            """
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
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()


    def check_user_permission(self, user, permission):
        conn = None
        try:
            conn = self.connect()
            if conn:
                cursor = conn.cursor()
            else:
                return -1
            query = "SELECT stat FROM user_permission WHERE usr=%s AND permission=%s"
            
            cursor.execute(query, (user, permission))
            result = cursor.fetchone()
            if result:
                stat = result[0]
                return stat == 1
            else:
                return False
        except Exception as e:
            print(f"Error checking user permission: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()



    def delete_record(self, id, user, date, now):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = """
            UPDATE record
            SET del_user = %s, 
                del_date = %s,
                deleted = 1
            WHERE id = %s AND editdate = %s;
            """
            cursor.execute(query, (user, now, id, date))
            conn.commit()
            self.update_last_modified_time(user)  # 更新最后修改时间
            return True
        except Exception as e:
            print(f"Error deleting record: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def delete_product(self, id, user, now):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = """
            UPDATE rug
            SET del_user = %s, 
                del_date = %s,
                deleted = 1
            WHERE id = %s AND deleted=0;
            """
            cursor.execute(query, (user, now, id))
            conn.commit()
            self.update_last_modified_time(user)  # 更新最后修改时间
            return True
        except Exception as e:
            print(f"Error deleting product/rug: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()


    def fetch_record_bef(self, id, date):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = """
            SELECT bef FROM record
            WHERE id=%s AND editdate=%s;
            """
            
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
            if conn and conn.is_connected():
                conn.close()


    def fetch_qty(self, id):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            query = """
            SELECT qty FROM rug
            WHERE id=%s and deleted=0;
            """
            
            # 执行查询操作
            cursor.execute(query, (id,))
            result = cursor.fetchone()
            if result:
                return result[0]  # 如果查询到结果，返回查询到的qty值
            else:
                return None  # 如果没有查询到结果，返回None
        except Exception as e:
            print(f"Error fetching qty: {e}")
            return None  # 如果出现异常，返回None
        finally:
            if conn and conn.is_connected():
                conn.close()  # 确保在最后关闭数据库连接



    def update_last_modified_time(self, user):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            # 获取当前时间
            current_time = datetime.datetime.now()
            # 准备更新time_log表的SQL语句
            update_query = """
            UPDATE time_log
            SET tim = %s, usr=%s
            WHERE title = 'last_modify';
            """
            # 执行SQL语句
            cursor.execute(update_query, (current_time, user))
            conn.commit()
        except Exception as e:
            print(f"An error occurred while updating the last modified time: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn and conn.is_connected():
                conn.close()

    def fetch_last_modified(self):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            fetch_query = """
            SELECT tim, usr FROM time_log
            WHERE title = 'last_modify'
            LIMIT 1;
            """
            cursor.execute(fetch_query)
            result = cursor.fetchone()
            if result:
                # 如果查询到结果，将其封装在字典中返回
                return {'time': result[0], 'user': result[1]}
            else:
                # 如果没有查询到结果，返回一个空字典
                return {}
        except Exception as e:
            print(f"An error occurred while fetching the last modified time: {e}")
            return {}
        finally:
            if conn and conn.is_connected():
                conn.close()

    def fetch_show_about(self):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            fetch_query = """
            SELECT tim, usr FROM time_log
            WHERE title = 'show_about'
            LIMIT 1;
            """
            cursor.execute(fetch_query)
            result = cursor.fetchone()
            if result:
                # 如果查询到结果，将其封装在字典中返回
                return {'time': result[0], 'user': result[1]}
            else:
                # 如果没有查询到结果，返回一个空字典
                return {}
        except Exception as e:
            print(f"An error occurred while fetching the last modified time: {e}")
            return {}
        finally:
            if conn and conn.is_connected():
                conn.close()

    def fetch_version(self):
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            fetch_query = """
            SELECT tim, usr FROM time_log
            WHERE title = 'version'
            LIMIT 1;
            """
            cursor.execute(fetch_query)
            result = cursor.fetchone()
            if result:
                # 如果查询到结果，将其封装在字典中返回
                return {'time': result[0], 'user': result[1]}
            else:
                # 如果没有查询到结果，返回一个空字典
                return {}
        except Exception as e:
            print(f"An error occurred while fetching the last modified time: {e}")
            return {}
        finally:
            if conn and conn.is_connected():
                conn.close()

    def show_message(self, type, title, message):
        # 创建一个消息框
        message_box = QMessageBox()
        if type == 'info':
            message_box.setIcon(QMessageBox.Information)
        elif type == 'warn':
            message_box.setIcon(QMessageBox.Warning)

        # 设置消息框的窗口图标
        if getattr(sys, 'frozen', False):
            # 打包后的情况
            application_path = sys._MEIPASS
        else:
            # 从源代码运行的情况
            application_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(application_path, 'vivastock.ico')
        message_box.setWindowIcon(QIcon(icon_path))

        message_box.setText(message)
        message_box.setWindowTitle(title)
        message_box.setStandardButtons(QMessageBox.Ok)
        
        # 设置消息框始终在最上层显示
        message_box.setWindowFlags(message_box.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 显示消息框
        message_box.exec_()

        
    def exit_with_conn_error(self):
        self.show_message('warn', '错误', '数据库连接失败。\n\n获取备用IP地址失败，请检查网络连接。\n\n1. 楼上办公室用户请确认电脑已连接PEPLINK网络\n2. 楼下前台用户请确认电脑已连接VIVA LIFESTYLE网络\n3. 请确认办公室Helen电脑是否已开机并连接到PEPLINK网络')
        sys.exit(1)  # 终止程序





