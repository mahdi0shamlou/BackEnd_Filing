import pandas as pd
import mysql.connector
from mysql.connector import Error
import uuid

# Function to connect to MySQL database
def connect_to_db(host_name, db_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            database=db_name,
            user=user_name,
            password=user_password
        )
        print("MySQL Database connection was successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

# Function to insert users into the database

def insert_users(connection, users):
    try:
        cursor = connection.cursor()

        for index, row in users.iterrows():
            try:
                print(row['name'])
                # Generate a unique username
                username = f"{row['name'].replace(' ', '_').lower()}_{uuid.uuid4().hex[:8]}"
                query = """
                    INSERT INTO users (username, name, phone, password)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (username, row['name'], row['phone'], "123"))
            except Exception as e:
                print(e)
                continue
        connection.commit()
        print("Users inserted successfully.")
    except Error as err:
        print(f"Error: '{err}'")

# Main function
def main():
    # MySQL connection parameters
    host_name = '185.190.39.252'
    db_name = 'BackEndFiling'
    user_name = 'backend'
    user_password = 'ya mahdi'

    # CSV file path
    csv_file_path = 'user.csv'

    # Connect to MySQL database
    connection = connect_to_db(host_name, db_name, user_name, user_password)

    if connection:
        # Read CSV file
        try:
            users = pd.read_csv(csv_file_path)
            # Ensure columns are named 'name' and 'phone'
            users.columns = ['name', 'phone']
            insert_users(connection, users)
        except Exception as e:
            print(f"Error reading CSV or inserting data: {e}")

        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()
