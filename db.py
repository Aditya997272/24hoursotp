# db.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # .env फाईल लोड करतो (लोकल टेस्टिंगसाठी)

logger = logging.getLogger(__name__)

# ================= DATABASE CONFIG =================
DB_TYPE = os.getenv("DB_TYPE", "mysql")  # Render वर "postgres" टाक, लोकलसाठी "mysql"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306" if DB_TYPE == "mysql" else "5432")
DB_NAME = os.getenv("DB_NAME", "db_24hoursotp")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# ================= DATABASE CONNECTION =================
def get_db_connection():
    try:
        if DB_TYPE == "postgres":
            import psycopg2
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
        else:  # mysql
            import mysql.connector
            return mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                raise_on_warnings=True
            )
    except Exception as err:
        logger.error(f"Database connection failed: {err}")
        raise

# ================= DATABASE SETUP =================
def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users Table
    if DB_TYPE == "postgres":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            balance DECIMAL(12,2) DEFAULT 0.00,
            is_blocked BOOLEAN DEFAULT FALSE,
            referred_by BIGINT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            balance DECIMAL(12,2) DEFAULT 0.00,
            is_blocked TINYINT(1) DEFAULT 0,
            referred_by BIGINT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

    # Services Table
    if DB_TYPE == "postgres":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(100) NOT NULL,
            provider_service_code VARCHAR(50) NOT NULL,
            country_id INTEGER DEFAULT 22,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE (service_name)
        );
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INT AUTO_INCREMENT PRIMARY KEY,
            service_name VARCHAR(100) NOT NULL,
            provider_service_code VARCHAR(50) NOT NULL,
            country_id INT DEFAULT 22,
            is_active TINYINT(1) DEFAULT 1,
            UNIQUE KEY unique_service (service_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

    # Servers Table
    if DB_TYPE == "postgres":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id SERIAL PRIMARY KEY,
            service_id INTEGER NOT NULL,
            server_number INTEGER NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
            UNIQUE (service_id, server_number)
        );
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            service_id INT NOT NULL,
            server_number INT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            is_active TINYINT(1) DEFAULT 1,
            FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
            UNIQUE KEY unique_server (service_id, server_number)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

    # Orders Table
    if DB_TYPE == "postgres":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            service_id INTEGER NOT NULL,
            server_id INTEGER NOT NULL,
            phone_number VARCHAR(20),
            activation_id VARCHAR(100),
            status VARCHAR(50) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (service_id) REFERENCES services(id),
            FOREIGN KEY (server_id) REFERENCES servers(id)
        );
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            service_id INT NOT NULL,
            server_id INT NOT NULL,
            phone_number VARCHAR(20),
            activation_id VARCHAR(100),
            status ENUM('PENDING', 'NUMBER_RECEIVED', 'OTP_RECEIVED', 'CANCELLED', 'TIMEOUT', 'FAILED') DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (service_id) REFERENCES services(id),
            FOREIGN KEY (server_id) REFERENCES servers(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

    # Transactions Table
    if DB_TYPE == "postgres":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            type VARCHAR(10) NOT NULL,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            type ENUM('CREDIT', 'DEBIT') NOT NULL,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

    # Wallet Requests Table
    if DB_TYPE == "postgres":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS wallet_requests (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            screenshot_url VARCHAR(255),
            status VARCHAR(50) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS wallet_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            screenshot_url VARCHAR(255),
            status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

    conn.commit()
    conn.close()
    logger.info("Database tables setup complete.")

# ================= USER FUNCTIONS =================
def add_or_get_user(user_id: int, referred_by: int = None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, referred_by) VALUES (%s, %s)", (user_id, referred_by))
    conn.commit()
    conn.close()

def get_user_balance(user_id: int) -> float:
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    conn.close()
    return float(row['balance']) if row else 0.0

def update_balance(user_id: int, amount: float, trans_type: str, description: str) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if trans_type == "DEBIT":
            cur.execute(
                "UPDATE users SET balance = balance - %s WHERE user_id = %s AND balance >= %s",
                (amount, user_id, amount)
            )
            success = cur.rowcount > 0
        else:
            cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
            success = True

        if success:
            cur.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (%s, %s, %s, %s)",
                (user_id, abs(amount), trans_type, description)
            )
        conn.commit()
        return success
    except Exception as e:
        logger.error(f"Balance update failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def is_user_blocked(user_id: int) -> bool:
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT is_blocked FROM users WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    conn.close()
    return bool(row and row['is_blocked'])

def set_user_block(user_id: int, block: bool):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_blocked = %s WHERE user_id = %s", (int(block), user_id))
    conn.commit()
    conn.close()

# ================= SERVICES & SERVERS =================
def get_services():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, service_name, provider_service_code FROM services WHERE is_active = 1")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_active_servers(service_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, server_number, price FROM servers WHERE service_id = %s AND is_active = 1", (service_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_servers_for_admin(service_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, server_number, price, is_active FROM servers WHERE service_id = %s", (service_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def toggle_server(server_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE servers SET is_active = NOT is_active WHERE id = %s", (server_id,))
    conn.commit()
    conn.close()

# ================= ORDERS =================
def create_order(user_id: int, service_id: int, server_id: int, phone: str, activation_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (user_id, service_id, server_id, phone_number, activation_id, status)
        VALUES (%s, %s, %s, %s, %s, 'PENDING')
    """, (user_id, service_id, server_id, phone, activation_id))
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id

def update_order_status(order_id: int, status: str, otp: str = None):
    conn = get_db_connection()
    cur = conn.cursor()
    if otp:
        cur.execute("UPDATE orders SET status = %s, otp = %s WHERE id = %s", (status, otp, order_id))
    else:
        cur.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
    conn.commit()
    conn.close()

# ================= WALLET REQUESTS =================
def create_recharge_request(user_id: int, amount: float, screenshot_url: str = None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO wallet_requests (user_id, amount, screenshot_url)
        VALUES (%s, %s, %s)
    """, (user_id, amount, screenshot_url))
    req_id = cur.lastrowid
    conn.commit()
    conn.close()
    return req_id

# ================= INITIAL SETUP =================
setup_database()