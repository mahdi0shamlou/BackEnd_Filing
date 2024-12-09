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
        self.close()

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
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist.")
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("User name or password is wrong.")
            else:
                print(err)

    def create_users_table(self):
        #----------------------------
        #---------- create Users table
        # ----------------------------
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
        #----------------------------
        #---------- End Users table
        # ----------------------------
        #----------------------------
        #---------- Creates files table
        # ----------------------------
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Posts (
            id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            status INT NOT NULL,
            token VARCHAR(191) NOT NULL UNIQUE,
            number VARCHAR(191) NOT NULL,
            city  BIGINT(3) NOT NULL,
            city_text  VARCHAR(191) NOT NULL,
            mahal  BIGINT(5) NOT NULL,
            mahal_text  VARCHAR(191) NOT NULL,
            type BIGINT(3) NOT NULL,
            type_text  VARCHAR(191) NOT NULL,
            title VARCHAR(191) NOT NULL,
            price BIGINT(30) NOT NULL,
            price_two BIGINT(30) NOT NULL,
            meter BIGINT(30) NOT NULL,
            desck TEXT,
            map TEXT,
            Images TEXT,
            details TEXT,
            Otagh TINYINT UNSIGNED,
            Make_years BIGINT(5),
            PARKING BOOLEAN DEFAULT FALSE,
            ELEVATOR BOOLEAN DEFAULT FALSE,
            CABINET BOOLEAN DEFAULT FALSE,
            BALCONY BOOLEAN DEFAULT FALSE,
            date_created_persian VARCHAR(20),
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()


        '''
        create_table_query = """
        CREATE TABLE IF NOT EXISTS PostFileSell (
            id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            status INT NOT NULL,
            token VARCHAR(191) NOT NULL UNIQUE,
            number VARCHAR(191) NOT NULL,
            city  BIGINT(3) NOT NULL,
            city_text  VARCHAR(191) NOT NULL,
            mahal  BIGINT(5) NOT NULL,
            mahal_text  VARCHAR(191) NOT NULL,
            type BIGINT(3) NOT NULL,
            title VARCHAR(191) NOT NULL,
            price BIGINT(30) NOT NULL,
            price_per_meter BIGINT(30) NOT NULL,
            meter BIGINT(30) NOT NULL,
            desck TEXT,
            map TEXT,
            Images TEXT,
            details TEXT,
            Otagh TINYINT UNSIGNED,
            Make_years BIGINT(5),
            PARKING BOOLEAN DEFAULT FALSE,
            ELEVATOR BOOLEAN DEFAULT FALSE,
            CABINET BOOLEAN DEFAULT FALSE,
            BALCONY BOOLEAN DEFAULT FALSE,
            date_created_persian VARCHAR(20),
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS PostFileRent (
            id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            status INT NOT NULL,
            token VARCHAR(191) NOT NULL UNIQUE,
            number VARCHAR(191) NOT NULL,
            city  BIGINT(3) NOT NULL,
            city_text  VARCHAR(191) NOT NULL,
            mahal  BIGINT(5) NOT NULL,
            mahal_text  VARCHAR(191) NOT NULL,
            type BIGINT(3) NOT NULL,
            title VARCHAR(191) NOT NULL,
            price BIGINT(30) NOT NULL,
            rent BIGINT(30) NOT NULL,
            meter BIGINT(30) NOT NULL,
            desck TEXT,
            map TEXT,
            Images TEXT,
            details TEXT,
            Otagh TINYINT UNSIGNED,
            Make_years BIGINT(5),
            PARKING BOOLEAN DEFAULT FALSE,
            ELEVATOR BOOLEAN DEFAULT FALSE,
            CABINET BOOLEAN DEFAULT FALSE,
            BALCONY BOOLEAN DEFAULT FALSE,
            date_created_persian VARCHAR(20),
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        '''
        #----------------------------
        #---------- End files table
        # ----------------------------
        #----------------------------
        #---------- Create Cities and Mahal table
        # ----------------------------
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Cities (
            id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            name VARCHAR(191) NOT NULL UNIQUE,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP, 
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Neighborhoods (
            id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            name VARCHAR(191) NOT NULL,
            city_id BIGINT(20) UNSIGNED NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            FOREIGN KEY (city_id) REFERENCES Cities(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Neighborhoods_For_Scrapper (
            id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
            name VARCHAR(191) NOT NULL,
            scrapper_id BIGINT(20) UNSIGNED NOT NULL,            
            neighborhoods_id BIGINT(20) UNSIGNED NOT NULL,
            city_id BIGINT(20) UNSIGNED NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            FOREIGN KEY (neighborhoods_id) REFERENCES Neighborhoods(id) ON DELETE CASCADE,
            FOREIGN KEY (city_id) REFERENCES Cities(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        #----------------------------
        #---------- End Cities and Mahal table
        # ----------------------------
        #----------------------------
        #---------- Create Notes table
        # ----------------------------
        create_table_query = """
                CREATE TABLE IF NOT EXISTS Notes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id_created BIGINT(20) UNSIGNED NOT NULL,
                    file_id_created BIGINT(20) UNSIGNED NOT NULL,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NULL DEFAULT NULL,
                    FOREIGN KEY (user_id_created) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (file_id_created) REFERENCES Posts(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        #----------------------------
        #---------- End Notes table
        # ----------------------------
        #----------------------------
        #---------- Create ZoonKan table
        # ----------------------------
        create_table_query = """
            CREATE TABLE IF NOT EXISTS ZoonKan (
                id BIGINT(20) AUTO_INCREMENT PRIMARY KEY,
                user_id_created BIGINT(20) UNSIGNED NOT NULL,
                name VARCHAR(191) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (user_id_created) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS FilesInZoonKan (
                id BIGINT(20) AUTO_INCREMENT PRIMARY KEY,
                user_id_created BIGINT(20) UNSIGNED NOT NULL,
                file_id_created BIGINT(20) UNSIGNED NOT NULL,
                zoonkan_id_in BIGINT(20) UNSIGNED NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (user_id_created) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (file_id_created) REFERENCES Posts(id) ON DELETE CASCADE,
                FOREIGN KEY (zoonkan_id_in) REFERENCES ZoonKan(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        #----------------------------
        #---------- End Notes table
        # ----------------------------
        #----------------------------
        #---------- Start Classifictions
        # ----------------------------
        create_table_query = """
            CREATE TABLE IF NOT EXISTS Classifictions (
                id BIGINT(20) AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(191) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS Classifictions_Neighborhoods (
                id BIGINT(20) AUTO_INCREMENT PRIMARY KEY,
                classifiction_id BIGINT(20) NOT NULL,
                neighborhood_id BIGINT(20) UNSIGNED NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (classifiction_id) REFERENCES Classifictions(id) ON DELETE CASCADE,
                FOREIGN KEY (neighborhood_id) REFERENCES Neighborhoods(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS Classifictions_Types (
                id BIGINT(20) AUTO_INCREMENT PRIMARY KEY,
                classifiction_id BIGINT(20) NOT NULL,
                type INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (classifiction_id) REFERENCES Classifictions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()

        create_table_query = """
            CREATE TABLE IF NOT EXISTS Types_file (
                id BIGINT(20) AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(191) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        #----------------------------
        #---------- End classifire
        # ----------------------------
        #----------------------------
        #---------- Start user Access
        # ----------------------------
        create_table_query = """
            CREATE TABLE IF NOT EXISTS User_Access (
                id BIGINT(20) AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT(20) UNSIGNED NOT NULL,
                classifictions_id BIGINT(20) UNSIGNED NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NULL DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (classifictions_id) REFERENCES Classifictions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
        self.cursor.execute(create_table_query)
        self.connection.commit()


    def close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    db_manager = DatabaseManager()
