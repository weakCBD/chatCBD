import mysql.connector
from mysql.connector import Error

class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def _connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"Error: {e}")
            return None

    def execute_query(self, query, params=None):
        connection = self._connect()
        if connection is None:
            return None
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    def fetch_one(self, query, params=None):
        connection = self._connect()
        if connection is None:
            return None
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()

    def fetch_all(self, query, params=None):
        connection = self._connect()
        if connection is None:
            return None
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()