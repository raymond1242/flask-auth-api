import os
import psycopg2
from dotenv import load_dotenv
from flask.cli import FlaskGroup
from app import app

load_dotenv()
cli = FlaskGroup(app)

db_name = os.getenv('POSTGRES_DB')
db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_port = os.getenv('POSTGRES_PORT', 5432)

def close_connection_and_cursor(conn, cur):
    cur.close()
    conn.close()

def get_connection_and_cursor():
    conn = psycopg2.connect(
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cur = conn.cursor()
    return conn, cur

def get_user_by_email(email):
    conn, cur = get_connection_and_cursor()
    cur.execute(f"SELECT * FROM users WHERE email='{email}';")
    user = cur.fetchone()
    close_connection_and_cursor(conn, cur)
    print(user)
    return user

def create_user(name, email, password):
    conn, cur = get_connection_and_cursor()
    cur.execute(f"INSERT INTO users (name, email, password) VALUES ('{name}', '{email}', '{password}');")
    conn.commit()
    close_connection_and_cursor(conn, cur)

def create_product(name, price, quantity):
    conn, cur = get_connection_and_cursor()
    cur.execute(f"INSERT INTO products (name, price, quantity) VALUES ('{name}', '{price}', '{quantity}');")
    conn.commit()
    close_connection_and_cursor(conn, cur)

def get_product_by_name(name):
    conn, cur = get_connection_and_cursor()
    cur.execute(f"SELECT * FROM products WHERE name='{name}';")
    product = cur.fetchall()
    close_connection_and_cursor(conn, cur)
    print(product)
    return product

def get_product_by_id(id):
    conn, cur = get_connection_and_cursor()
    cur.execute(f"SELECT * FROM products WHERE id='{id}';")
    product = cur.fetchone()
    close_connection_and_cursor(conn, cur)
    print(product)
    return product

def update_product_by_id(id, name, price, quantity):
    conn, cur = get_connection_and_cursor()
    cur.execute(f"UPDATE products SET name='{name}', price='{price}', quantity='{quantity}' WHERE id='{id}';")
    conn.commit()
    close_connection_and_cursor(conn, cur)
    return get_product_by_id(id), True

def delete_product_by_id(id):
    conn, cur = get_connection_and_cursor()
    cur.execute(f"DELETE FROM products WHERE id='{id}';")
    conn.commit()
    close_connection_and_cursor(conn, cur)
    return True


@cli.command('create_db')
def create_db():
    conn, cur = get_connection_and_cursor()
    cur.execute('CREATE DATABASE flask;')
    conn.commit()
    close_connection_and_cursor(conn, cur)
    print('Database created successfully')

@cli.command('create_tables')
def create_tables():
    conn, cur = get_connection_and_cursor()
    cur.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            email VARCHAR(50) UNIQUE,
            password VARCHAR(100),
            last_verification_token VARCHAR(100)
        );
    ''')
    cur.execute('''
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            price FLOAT,
            quantity INTEGER
        );
    ''')
    conn.commit()
    close_connection_and_cursor(conn, cur)
    print('Tables created successfully')


if __name__ == '__main__':
    cli()
