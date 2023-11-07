import pyodbc

class DatabaseManager:
    def __init__(self):
        self.server = 'de-2-111-db.database.windows.net'
        self.database = 'de-2-111'
        self.username = 'dbadmin'
        self.password = 'pa$$w0rd'
        self.driver = '{ODBC Driver 17 for SQL Server}'
        self.conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;'  
        )
        self.cursor = self.conn.cursor()

