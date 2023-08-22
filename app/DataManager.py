import sqlite3


# Set to reset table structure on next db access (remember to turn off again...)
andDrop = False

db_name = 'database'
db_user = 'username'
db_pass = 'secret'
db_host = 'db'
db_port = '5432'

# Connecto to the database
db_string = 'postgresql://{}:{}@{}:{}/{}'.format(
    db_user, db_pass, db_host, db_port, db_name)


class DataManager:
    def __init__(self, db_path):
        """Initializes the DataManager with a database file path."""
        self.db = create_engine(db_string)

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
                    description_head TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                    category TEXT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def get_transactions(self, user_id, ts_id, page, limit, negative_only: bool):

        if negative_only:
            cursor = self.conn.execute(
                'SELECT * FROM transactions WHERE user_id = ? AND ts_id = ? AND amount < 0 LIMIT ? OFFSET ?', (user_id, ts_id, limit, page*limit))
            return cursor.fetchall()
            # Retrieve only positive transactions
        else:
            # Retrieve all transactions
            cursor = self.conn.execute(
                'SELECT * FROM transactions WHERE user_id = ? AND ts_id = ? LIMIT ? OFFSET ?', (user_id, ts_id, limit, page*limit))
            return cursor.fetchall()

    def get_transactions_to_process(self, user_id, ts_id, page, limit):
        """Returns transactions filtered by a given id + user_id."""
        print(f"get_transactions(self, {user_id}, {ts_id})")
        cursor = self.conn.execute(
            'SELECT * FROM transactions WHERE user_id = ? AND ts_id = ? AND status = \'pending\' LIMIT ? OFFSET ?', (user_id, ts_id, limit, page*limit))
        return cursor.fetchall()

    def set_transaction_category(self, t_id, category):
        with self.conn:
            cursor = self.conn.execute(
                'UPDATE transactions SET category = ?, status =? WHERE t_id = ?', (
                    category, 'complete', t_id))
            return cursor.lastrowid

    def reset_transaction(self, t_id):
        """Returns transactions filtered by a given id + user_id."""
        cursor = self.conn.execute(
            'UPDATE transactions SET status = \'pending\', category = NULL WHERE t_id = ?', (t_id,))
        self.conn.commit()
        return cursor.lastrowid

    def reset_transaction_set(self, ts_id):
        """Returns transactions filtered by a given id + user_id."""
        cursor = self.conn.execute(
            "UPDATE transactions SET status = 'pending', category = NULL WHERE ts_id = ?", (ts_id,))
        self.conn.commit()
        return cursor.rowcount

    def get_transaction(self, user_id, id):
        """Returns transactions filtered by a given id + user_id."""
        cursor = self.conn.execute(
            'SELECT * FROM transactions WHERE user_id = ? AND id = ?', (user_id, id))
        return cursor.fetchall()

    def get_transaction_sets_by_session(self, user_id, ts_id):
        """Returns transactions filtered by a given user_id."""
        cursor = self.conn.execute(
            'SELECT ts_id, COUNT(*) FROM transactions WHERE user_id = ? GROUP BY ts_id', (user_id, ts_id))
        return cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()
