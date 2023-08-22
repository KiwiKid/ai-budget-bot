from sqlalchemy import create_engine, text
import os

# Set to reset table structure on next db access (remember to turn off again...)
andDrop = False

user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
db_name = os.getenv('DATABASE_NAME')
host = os.getenv('DATABASE_HOST')
db_port = '5432'

# Connecto to the database
db_string = 'postgresql://{}:{}@{}:{}/{}'.format(
    user, password, host, db_port, db_name)


class DataManager:
    def __init__(self, db_path):
        """Initializes the DataManager with a database file path."""
        self.engine = create_engine(db_string)
        self.conn = self.engine.connect()

    def save_header(self, header):
        """Saves a header to the headers table."""
        query = text('''
            INSERT INTO headers (ts_id, user_id, amount_head, date_head, description_head) 
            VALUES (:ts_id, :user_id, :amount_head, :date_head, :description_head)
        ''')
        result = self.conn.execute(query,
                                   {
                                       'ts_id': header['ts_id'],
                                       'user_id': header['user_id'],
                                       'amount_head': header['amount_head'],
                                       'date_head': header['date_head'],
                                       'description_head': "|".join(
                                           header['description_head'])
                                   }
                                   )
        return result.lastrowid

    def save_transaction(self, t_id: str, ts_id: str, user_id: str, amount: str, date: str, description: str, status: str):
        """Saves a transaction to the transactions table."""
        print(
            f"save_transaction(self, status:{status} t_id:{t_id}, ts_id:{ts_id} user_id:{user_id} amount:{amount} date:{date} description:{description})")

        query = text('''
                INSERT INTO transactions (t_id, ts_id, user_id, amount, date, description, status) 
                VALUES (:t_id, :ts_id, :user_id, :amount, :date, :description, :status)
            ''')

        result = self.conn.execute(query,
                                   {
                                       't_id': t_id,
                                       'ts_id': ts_id,
                                       'user_id': user_id,
                                       'amount': amount,
                                       'date': date,
                                       'description': description,
                                       'status': status
                                   })
        return result.lastrowid

    def get_header_by_session(self, user_id):
        """Returns headers filtered by a given userId."""
        query = text('SELECT * FROM headers WHERE user_id = :user_id')
        result = self.conn.execute(query, {'user_id': user_id})
        return result.fetchall()

    def get_transactions(self, user_id, ts_id, page, limit, negative_only: bool):
        offset = page * limit

        if negative_only:
            query = text('''
                SELECT * FROM transactions 
                WHERE user_id = :user_id AND ts_id = :ts_id AND amount < 0 
                LIMIT :limit OFFSET :offset
            ''')
            result = self.conn.execute(
                query, {'user_id': user_id, 'ts_id': ts_id, 'limit': limit, 'offset': offset})
        else:
            query = text('''
                SELECT * FROM transactions 
                WHERE user_id = :user_id AND ts_id = :ts_id 
                LIMIT :limit OFFSET :offset
            ''')
            result = self.conn.execute(
                query, {'user_id': user_id, 'ts_id': ts_id, 'limit': limit, 'offset': offset})

        return result.fetchall()

    def get_transactions_to_process(self, user_id, ts_id, page, limit):
        """Returns transactions filtered by a given id + user_id."""
        print(f"get_transactions(self, {user_id}, {ts_id})")

        offset = page * limit
        query = text('''
            SELECT * FROM transactions 
            WHERE user_id = :user_id AND ts_id = :ts_id AND status = 'pending' 
            LIMIT :limit OFFSET :offset
        ''')
        result = self.conn.execute(
            query, {'user_id': user_id, 'ts_id': ts_id, 'limit': limit, 'offset': offset})

        return result.fetchall()

    def set_transaction_category(self, t_id, category):
        query = text('''
            UPDATE transactions 
            SET category = :category, status = 'complete' 
            WHERE t_id = :t_id
        ''')
        result = self.conn.execute(
            query, {'category': category,  't_id': t_id})

        return result.lastrowid

    def reset_transaction(self, t_id):
        """Resets transaction status and category based on transaction id."""
        query = text('''
            UPDATE transactions 
            SET status = 'pending', category = NULL 
            WHERE t_id = :t_id
        ''')
        result = self.conn.execute(query, {'t_id': t_id})
        return result.lastrowid

    def reset_transaction_set(self, ts_id):
        """Resets transaction status and category based on transaction set id."""
        query = text('''
            UPDATE transactions 
            SET status = 'pending', category = NULL 
            WHERE ts_id = :ts_id
        ''')
        result = self.conn.execute(query, ts_id=ts_id)
        return result.rowcount

    def get_transaction(self, user_id, t_id):
        """Returns transactions filtered by a given user_id and transaction id."""
        query = text('''
            SELECT * FROM transactions 
            WHERE user_id = :user_id AND t_id = :t_id
        ''')
        result = self.conn.execute(query, {'user_id': user_id, 't_id': t_id})
        return result.fetchall()

    def get_transaction_sets_by_session(self, user_id):
        """Returns transactions filtered by a given user_id."""
        query = text('''
            SELECT ts_id, COUNT(*) 
            FROM transactions 
            WHERE user_id = :user_id
            GROUP BY ts_id
        ''')
        result = self.conn.execute(query, {'user_id': user_id})
        return result.fetchall()

    def close(self):
        """Close the database connection."""
        # Assuming you have a session or connection object, use that to close the connection
        self.conn.close()
