import mysql.connector
from datetime import datetime as dt

from App.Config.config import DB_NAME, DB_HOST, DB_PASS, DB_USER, CLOUD_ID

from telebot import TeleBot

class DB:
    def __init__(self, bot: TeleBot = None):
        self.bot = bot
        # Here you can set a connection to a database likely on any relational database management system (RDBMS) like MySQL, PostgreSQL, SQLite, etc.
        # self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        self.cursor = self.conn.cursor()

    def send_backup(self):
        try:
            # Pegar o sql com o dump do banco de dados
            # self.bot.send_document(CLOUD_ID, open(DB_NAME, 'rb'), caption='Backup database')
            pass
        except Exception as e:
            print(e)

    def dictify_query(self, cursor: mysql.connector.cursor.MySQLCursor, columns: list = None):
        """ Returns a list of dictionaries from a cursor object """
        try:
            if columns:
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(e)
            # return generic object with result
            return []
            

    def dictify_result(self, cursor: mysql.connector.cursor.MySQLCursor, result: list):
        """ Returns a list of dictionaries from a cursor object """
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in result]

    # Generic methods for CRUD

    def insert(self, table: str, data: dict):
        """ Example: insert('users', {'userid': userid, 'lang': lang}) """
        try:
            # Use %s como placeholder para MariaDB/MySQL
            sql = f'INSERT INTO {table} ({",".join(data.keys())}) VALUES ({",".join(["%s" for _ in data.values()])})'
            self.cursor.execute(sql, list(data.values()))
            self.conn.commit()
            self.send_backup()
            return self.cursor.lastrowid # returns the row id of the cursor object, or None if no row was inserted or an error occurred.
        except Exception as e:
            print(e)
            return False
    
    def select(self, table: str, columns: list, where = None, final: str = None):
        # Example: select('users', ['userid', 'lang'], 'userid = ?', [userid])
        # Example multiple where: select('users', ['userid', 'lang'], "userid = '850446631' AND lang = 'pt' ")
        # Example get all from table: select('users', ['*'])
        # Check if the table has the column 'deleted_at'
        self.cursor.reset()
        self.cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'deleted_at'")
        column_exists = self.cursor.fetchone()

        if column_exists:
            sql = f"SELECT {','.join(columns)}"
            sql += f" FROM {table}"
            sql += f" WHERE {where} AND deleted_at IS NULL" if where else " WHERE deleted_at IS NULL"
            sql += f" {final}" if final else ""
        else:
            sql = f"SELECT {','.join(columns)}"
            sql += f" FROM {table}"
            sql += f" WHERE {where}" if where else ""
            sql += f" {final}" if final else ""
            
        # print('\n\n', sql)
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return [dict(zip([key[0] for key in self.cursor.description], row)) for row in rows]
    
    def select_one(self, table: str, columns: list, where: str = None):
        """ Example: select_one('users', ['userid', 'lang'], 'userid = ?', [userid]) """
        result = self.select(table, columns, where)
        # return result[0] if result else {}
        return result[0] if result else None
    
    def update(self, table: str, data: dict, where: str) -> bool:
        # Example: update('users', {'lang': lang}, 'userid = ?', [userid])
        # Example multiple where: update('users', {'lang': lang}, f"userid = {userid} AND lang = {lang}")
        try:
            sql = f'UPDATE {table} SET {",".join([f"{column} = %s" for column in data.keys()])}' + (f' WHERE {where}' if where else '')
            # print('\n\n SQL:', sql)
            status = self.cursor.execute(sql, list(data.values()))
            # print('| Status do Update:', status)
            # print('| Rowcount:', self.cursor.rowcount)
            self.conn.commit()
            self.send_backup()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(e)
            return False
        

    def delete(self, table: str, where: str = None, values: list = None):
        # Example: delete('users', 'userid = ?', [userid])
        # Example multiple where: delete('users', 'userid = ? AND lang = ?', [userid, lang])
        self.cursor.execute(f'DELETE FROM {table}' + (f' WHERE {where}' if where else ''), values)
        self.conn.commit()
        self.send_backup()
        return self.cursor.rowcount > 0