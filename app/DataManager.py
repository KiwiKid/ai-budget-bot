import sqlite3

andDrop = False


class DataManager:
    def __init__(self, db_path):
        """Initializes the DataManager with a database file path."""
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create tables if they don't exist."""
        with self.conn:
            if andDrop:
                self.conn.execute('''
                    DROP TABLE IF EXISTS headers;
                ''')

            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS headers (
                    ts_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    amount_head TEXT NOT NULL,
                    date_head TEXT NOT NULL,
                    description_head TEXT NOT NULL
                )
            ''')

            if andDrop:
                self.conn.execute('''
                    DROP TABLE IF EXISTS transactions;
                ''')

            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    t_id TEXT NOT NULL,
                    ts_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    status TEXT NOT NULL,
                    category TEXT NUL
                )
            ''')

    def save_header(self, header):
        """Saves a header to the headers table."""
        with self.conn:
            cursor = self.conn.execute(
                'INSERT INTO headers (ts_id, user_id, amount_head, date_head, description_head) VALUES (?, ?, ?, ?, ?)', (
                    header['ts_id'], header['user_id'], header['amount_head'], header['date_head'], "|".join(header['description_head'])))
            return cursor.lastrowid

    def save_transaction(self, t_id: str, ts_id: str, user_id: str, amount: str, date: str, description: str, status: str):
        """Saves a transaction to the transactions table."""
        with self.conn:
            print(
                f"save_transaction(self, status:{status} t_id:{t_id}, ts_id:{ts_id} user_id:{user_id} amount:{amount} date:{date} description:{description})")

            cursor = self.conn.execute('INSERT INTO transactions (t_id, ts_id, user_id, amount, date, description, status) VALUES (?, ?, ?, ?, ?, ?, ?)', (
                t_id, ts_id,  user_id, amount, date, description, status))
            return cursor.lastrowid

    def get_header_by_session(self, user_id):
        """Returns headers filtered by a given userId."""
        cursor = self.conn.execute(
            'SELECT * FROM headers WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

    def get_transactions(self, user_id, ts_id, limit):
        """Returns transactions filtered by a given id + user_id."""
        print(f"get_transactions(self, {user_id}, {ts_id})")
        cursor = self.conn.execute(
            'SELECT * FROM transactions WHERE user_id = ? AND ts_id = ? LIMIT ?', (user_id, ts_id, limit))
        return cursor.fetchall()

    def get_transactions_to_process(self, user_id, ts_id, limit):
        """Returns transactions filtered by a given id + user_id."""
        print(f"get_transactions(self, {user_id}, {ts_id})")
        cursor = self.conn.execute(
            'SELECT * FROM transactions WHERE user_id = ? AND ts_id = ? AND status = \'pending\' LIMIT ?', (user_id, ts_id, limit))
        return cursor.fetchall()

    def set_transaction_category(self, t_id, category):
        with self.conn:
            cursor = self.conn.execute(
                'UPDATE transactions SET category = ?, status =? WHERE t_id = ?', (
                    category, 'complete', t_id))
            return cursor.lastrowid

    def get_transaction(self, user_id, id):
        """Returns transactions filtered by a given id + user_id."""
        cursor = self.conn.execute(
            'SELECT * FROM transactions WHERE user_id = ? AND id = ?', (user_id, id))
        return cursor.fetchall()

    def get_transactions_by_session(self, user_id):
        """Returns transactions filtered by a given user_id."""
        cursor = self.conn.execute(
            'SELECT * FROM transactions WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()
