from datetime import datetime
import os
from pathlib import Path
import json
import sqlite3
import requests
#export API_TOKEN='your_secure_token_here'
#set API_TOKEN=your_secure_token_here

token = os.environ.get("API_TOKEN")

class Database:
    def __init__(self, db_path = "allegro.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()

    def init_database(self):

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOTE EXISTS orders (
                allegro_order_id TEXT PRIMARY KEY UNIQUE NOT NULL,
                status TEXT NOT NULL,
                buyer_login TEXT,
                buyer_email TEXT,
                total_price REAL,
                created_at TEXT,
                updated_at TEXT,
                synced_at TEXT,
                raw_data TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id TEXT,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            )
        ''')

        # Tabela logów synchronizacji
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_date TEXT NOT NULL,
                orders_fetched INTEGER,
                orders_updated INTEGER,
                success BOOLEAN,
                error_message TEXT
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_status ON orders(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_allegro_order_id ON orders(allegro_order_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON orders(created_at)')

        self.conn.commit()
        print("zainicjalizowano db")

        def save_order(self, order_data: dict) -> int:
            """Zapisuje lub aktualizuje zamówienie"""
            cursor = self.conn.cursor()

            allegro_id = order_data.get('id')
            status = order_data.get('status', 'NEW')
            buyer = order_data.get('buyer', {})
            summary = order_data.get('summary', {})

            now = datetime.now().isoformat()

            # Sprawdź czy zamówienie istnieje
            cursor.execute('SELECT id FROM orders WHERE allegro_order_id = ?', (allegro_id,))
            existing = cursor.fetchone()

            if existing:
                # Aktualizuj istniejące
                cursor.execute('''
                    UPDATE orders 
                    SET status = ?, buyer_login = ?, buyer_email = ?, 
                        total_price = ?, updated_at = ?, synced_at = ?, raw_data = ?
                    WHERE allegro_order_id = ?
                ''', (
                    status, buyer.get('login'), buyer.get('email'),
                    summary.get('totalToPay', {}).get('amount'),
                    now, now, json.dumps(order_data), allegro_id
                ))
                order_id = existing['id']

                # Usuń stare produkty i dodaj nowe
                cursor.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
            else:
                # Wstaw nowe
                cursor.execute('''
                    INSERT INTO orders 
                    (allegro_order_id, status, buyer_login, buyer_email, 
                     total_price, created_at, updated_at, synced_at, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    allegro_id, status, buyer.get('login'), buyer.get('email'),
                    summary.get('totalToPay', {}).get('amount'),
                    order_data.get('createdAt', now), now, now,
                    json.dumps(order_data)
                ))
                order_id = cursor.lastrowid

            # Zapisz produkty
            for item in order_data.get('lineItems', []):
                cursor.execute('''
                    INSERT INTO order_items 
                    (order_id, product_id, product_name, quantity, price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    order_id,
                    item.get('offer', {}).get('id'),
                    item.get('offer', {}).get('name'),
                    item.get('quantity'),
                    item.get('price', {}).get('amount')
                ))

            self.conn.commit()
            return order_id

        def log_sync(self, orders_fetched: int, orders_updated: int,
                     success: bool, error_message: str = None):
            """Loguj synchronizację"""
            cursor = self.conn.cursor()
            cursor.execute('''
                  INSERT INTO sync_log 
                  (sync_date, orders_fetched, orders_updated, success, error_message)
                  VALUES (?, ?, ?, ?, ?)
              ''', (datetime.now().isoformat(), orders_fetched, orders_updated, success, error_message))
            self.conn.commit()

        def get_orders_by_status(self, status: str) -> list[dict]:
            """Pobiera zamówienia o określonym statusie"""
            cursor = self.conn.cursor()
            cursor.execute('''
                  SELECT * FROM orders WHERE status = ?
                  ORDER BY created_at DESC
              ''', (status,))
            return [dict(row) for row in cursor.fetchall()]

        def update_order_status(self, allegro_order_id: str, new_status: str) -> bool:
            """Aktualizuje status zamówienia lokalnie"""
            cursor = self.conn.cursor()
            cursor.execute('''
                  UPDATE orders 
                  SET status = ?, updated_at = ?
                  WHERE allegro_order_id = ?
              ''', (new_status, datetime.now().isoformat(), allegro_order_id))
            self.conn.commit()
            return cursor.rowcount > 0

        def get_all_orders(self, limit: int = 100) -> list[dict]:
            """Pobiera wszystkie zamówienia"""
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]

        def close(self):
            if self.conn:
                self.conn.close()



class Calculate:
    def __init__(self):
        print('d')


def main():
    config = Config("config.json")
    print()

if __name__ == '__main__':
    main()
