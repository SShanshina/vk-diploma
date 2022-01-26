import psycopg2
from psycopg2 import OperationalError
from settings_file import DB_NAME, DB_USER, DB_USER_PASSWORD


def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print('Connection to PostgreSQL DB successful')
    except OperationalError as e:
        print(f'The error "{e}" occurred')
    return connection


connection = create_connection(
    DB_NAME, DB_USER, DB_USER_PASSWORD, '127.0.0.1', '5432'
)


def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print('Query executed successfully')
    except OperationalError as e:
        print(f'The error "{e}" occurred')


create_users_table = "CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, user_id integer unique," \
                     "user_name varchar, user_surname varchar);"

execute_query(connection, create_users_table)


def execute_insert_query(connection, users_list):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        user_records = ', '.join(['%s'] * len(users_list))
        query = f"INSERT INTO users (user_id, user_name, user_surname) VALUES {user_records}"
        cursor.execute(query, users_list)
        print('Insert query executed successfully')
    except OperationalError as e:
        print(f'The error "{e}" occurred')


def execute_read_query(connection):
    cursor = connection.cursor()
    result = None
    query = "SELECT user_id, user_name, user_surname FROM users"
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        print('Select query executed successfully')
        return result
    except OperationalError as e:
        print(f'The error "{e}" occurred')
