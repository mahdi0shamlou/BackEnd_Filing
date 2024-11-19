import mysql.connector
from mysql.connector import errorcode
import configparser


class DatabaseManager:
    def __init__(self, config_file='db_config.ini'):
        self.config = self.load_config(config_file)
        self.host = self.config['mysql']['host']
        self.user = self.config['mysql']['user']
        self.password = self.config['mysql']['password']
        self.database = self.config['mysql']['database']
        self.port = self.config['mysql'].getint('port')
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_users_table()

    def load_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print('s')
        except mysql.connector.Error as err:

            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist.")
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("User name or password is wrong.")
            else:
                print(err)

    def create_users_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            username VARCHAR(191) NOT NULL UNIQUE,
            password VARCHAR(191) NOT NULL,
            name VARCHAR(191),
            phone VARCHAR(191) NOT NULL UNIQUE,
            address TEXT,
            email VARCHAR(191),
            created_at TIMESTAMP NULL DEFAULT NULL,
            updated_at TIMESTAMP NULL DEFAULT NULL,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def select_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchone()

    def select_user_by_phone(self, phone):
        query = "SELECT * FROM users WHERE phone = %s"
        self.cursor.execute(query, (phone,))
        return self.cursor.fetchone()

    def insert_user(self, username, password, name, phone, address, email):
        query = """
        INSERT INTO users (username, password, name, phone, address, email, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        self.cursor.execute(query, (username, password, name, phone, address, email))
        self.connection.commit()

    def update_user_by_usename(self, username, new_name, new_email):
        query = """
                Update users set email = %s , name = %s where username = %s
                """
        self.cursor.execute(query, (new_email, new_name, username))
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

# Example usage:
#db_manager = DatabaseManager()
#db_manager.insert_user('johndoe', 'password123', 'John Doe', '1234567890', '123 Main St', 'john@example.com')
#user = db_manager.select_user_by_username('johndoe')
# print(user)
#db_manager.close()
