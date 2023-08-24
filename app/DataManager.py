from sqlalchemy import create_engine, text
import os
from datetime import datetime
from dateutil.parser import parse
import uuid
# Set to reset table structure on next db access (remember to turn off again...)
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
host = os.getenv('POSTGRES_HOST')
debug = os.getenv('DEBUG')
db_port = '5432'


# Connecto to the database
db_string = 'postgresql://{}:{}@{}:{}/{}'.format(
    user, password, host, db_port, db_name)

if debug:
    print(f"{db_string} {host}")


class DataManager:
    def __init__(self):
        """Initializes the DataManager with a database file path."""
        self.engine = create_engine(db_string)
        self.conn = self.engine.connect()

    def save_header(self, header):
        """Saves a header to the headers table."""
        try:
            query = text('''
                INSERT INTO headers (ts_id, user_id, amount_head, date_head, description_head, custom_rules, custom_categories) 
                VALUES (:ts_id, :user_id, :amount_head, :date_head, :description_head)
                RETURNING *
            ''')
            result = self.conn.execute(query,
                                       {
                                           'ts_id': header['ts_id'],
                                           'user_id': header['user_id'],
                                           'amount_head': header['amount_head'],
                                           'date_head': header['date_head'],
                                           'description_head': "|".join(
                                               header['description_head']),
                                           'custom_rules': header['custom_rules'],
                                           'custom_categories': header['custom_categories']
                                       }
                                       )

        except Exception as e:
            print(f"Error: {e}")

        self.conn.commit()

        return result.rowcount

    def save_transaction(self, t_id: str, ts_id: str, user_id: str, amount: str, date: str, description: str, status: str):
        """Saves a transaction to the transactions table."""
        print(
            f"save_transaction(self, status:{status} t_id:{t_id}, ts_id:{ts_id} user_id:{user_id} amount:{amount} date:{date} description:{description})"
        )

        query = text('''
                INSERT INTO transactions (t_id, ts_id, user_id, amount, date, description, status) 
                VALUES (:t_id, :ts_id, :user_id, :amount, :date, :description, :status)
                RETURNING *
            ''')

        try:
            datetime_object = parse(date)
            formatted_datetime = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            raise ValueError(
                f"Could not parse the date string: {date}. Error: {ve}")

        try:
            result = self.conn.execute(query,
                                       {
                                           't_id': t_id,
                                           'ts_id': ts_id,
                                           'user_id': user_id,
                                           'amount': amount,
                                           'date': formatted_datetime,
                                           'description': description,
                                           'status': status
                                       })

            if result.rowcount != 1:
                raise RuntimeError("Could not save transaction")

            self.conn.commit()

            return result
        except Exception as e:  # Catching a generic exception to log the actual error message
            raise ValueError(f"could not save record. Error: {e}")

    def get_header(self, user_id, ts_id):
        """Returns headers filtered by a given userId."""
        query = text(
            'SELECT * FROM headers WHERE user_id = :user_id AND ts_id = :ts_id')
        result = self.conn.execute(query, {'user_id': user_id, 'ts_id': ts_id})
        return result.fetchall()

    def get_transactions(self, user_id: uuid, ts_id: uuid, page: int, limit: int, negative_only: bool):
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
            ''')  #
            result = self.conn.execute(
                query, {'ts_id': ts_id, 'limit': limit, 'offset': offset, 'user_id': user_id, })

        res = result.fetchall()

        return res

    def get_transactions_to_process(self, user_id, ts_id, page, limit):
        """Returns transactions filtered by a given id + user_id."""
        print(f"get_transactions_to_process(self, {user_id}, {ts_id})")

        offset = page * limit
        query = text('''
            SELECT * FROM transactions 
            WHERE user_id = :user_id AND ts_id = :ts_id AND status = 'pending' 
            LIMIT :limit OFFSET :offset
        ''')
        result = self.conn.execute(
            query, {'user_id': user_id, 'ts_id': ts_id, 'limit': limit, 'offset': offset})

        print(
            f"get_transactions_to_process - Got {result.rowcount} to process for ts_id :{ts_id}")

        return result.fetchall()

    def set_transaction_category(self, t_id, category):
        query = text('''
            UPDATE transactions 
            SET category = :category, status = 'complete' 
            WHERE t_id = :t_id
        ''')
        result = self.conn.execute(
            query, {'category': category,  't_id': t_id})

        self.conn.commit()
        return result.lastrowid

    def reset_transaction(self, t_id):
        """Resets transaction status and category based on transaction id."""
        query = text('''
            UPDATE transactions 
            SET status = 'pending', category = NULL 
            WHERE t_id = :t_id
        ''')
        result = self.conn.execute(query, {'t_id': t_id})

        self.conn.commit()

        return result.lastrowid

    def reset_transaction_set(self, ts_id):
        """Resets transaction status and category based on transaction set id."""
        query = text('''
            UPDATE transactions 
            SET status = 'pending', category = NULL 
            WHERE ts_id = :ts_id
        ''')
        result = self.conn.execute(query, {'ts_id': ts_id})
        self.conn.commit()
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
            SELECT ts_id, COUNT(*), MIN(created_at) AS earliest_created_at
            FROM transactions 
            WHERE user_id = :user_id
            GROUP BY ts_id
        ''')
        result = self.conn.execute(query, {'user_id': user_id})
        return result.fetchall()

    def delete_transaction_set(self, ts_id):
        query = text('''
            DELETE
            FROM transactions 
            WHERE ts_id = :ts_id
        ''')
        result = self.conn.execute(query, {'ts_id': ts_id})
        return result.rowcount

    def close(self):
        """Close the database connection."""
        # Assuming you have a session or connection object, use that to close the connection
        self.conn.close()
