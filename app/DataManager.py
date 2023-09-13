from sqlalchemy import create_engine, text
import os
from datetime import datetime
from dateutil.parser import parse

from app.Header import Header
from app.transaction import Transaction
from typing import List, Tuple, Optional, NamedTuple, Dict, Any
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


class TransactionSet(NamedTuple):
    ts_id: str
    count: int
    total: int
    batch_name: str
    earliest_created_at: datetime
    first_date: datetime
    last_date: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TransactionSet to a JSON serializable dictionary."""
        return {
            "ts_id": str(self.ts_id),
            "batch_name": self.batch_name,
            "count": self.count,
            "total": self.total,
            "first_date": self.first_date.isoformat(),
            "last_date": self.last_date.isoformat(),
            "earliest_created_at": self.earliest_created_at.isoformat()

        }


class DataManager:
    def __init__(self):
        """Initializes the DataManager with a database file path."""
        self.engine = create_engine(db_string)
        self.conn = self.engine.connect()

    def upsert_header_name(self, header):
        """Upserts a header in the headers table based on ts_id."""
        try:
            print(f"upserting header\n {header}")
            query = text('''
                INSERT INTO headers (ts_id, user_id, batch_name) 
                VALUES (:ts_id, :user_id, :batch_name)
                ON CONFLICT (ts_id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    batch_name = EXCLUDED.batch_name
            ''')
            result = self.conn.execute(query,
                                       {
                                           'ts_id': header['ts_id'],
                                           'user_id': header['user_id'],
                                           'batch_name': header['batch_name']
                                       }
                                       )

            self.conn.commit()
            print(f"upserted header")
            return result.rowcount

        except Exception as e:
            print(f"Error upsert_header: {e}")
            return None

    def save_header(self, header):
        """Saves a header to the headers table."""
        try:
            print(f"saving headers\n {header}")
            query = text('''
                INSERT INTO headers (ts_id, user_id, amount_head, batch_name, date_head, description_head, custom_rules, custom_categories) 
                VALUES (:ts_id, :user_id, :amount_head, :date_head, :description_head, :custom_rules, :custom_categories)
            ''')
            result = self.conn.execute(query,
                                       {
                                           'ts_id': header['ts_id'],
                                           'batch_name': header['batch_name'],
                                           'user_id': header['user_id'],
                                           'amount_head': header['amount_head'],
                                           'date_head': header['date_head'],
                                           'description_head': header['description_head'],
                                           'custom_rules': header['custom_rules'],
                                           'custom_categories': header['custom_categories']
                                       }
                                       )

            self.conn.commit()
            print(f"saved header")
            return result.rowcount

        except Exception as e:
            print(f"Error save_header: {e}")
            return None

    def update_header(self, header):
        """Updates a header in the headers table based on ts_id."""
        try:
            print(f"updating header\n {header}")
            query = text('''
                UPDATE headers 
                SET 
                    user_id = :user_id, 
                    amount_head = :amount_head,
                    batch_name = :batch_name,
                    date_head = :date_head, 
                    description_head = :description_head,
                    custom_rules = :custom_rules,
                    custom_categories = :custom_categories
                WHERE ts_id = :ts_id
            ''')
            result = self.conn.execute(query,
                                       {
                                           'ts_id': header['ts_id'],
                                           'batch_name': header['batch_name'],
                                           'user_id': header['user_id'],
                                           'amount_head': header['amount_head'],
                                           'date_head': header['date_head'],
                                           'description_head': header['description_head'],
                                           'custom_rules': header['custom_rules'],
                                           'custom_categories': header['custom_categories']
                                       }
                                       )

            self.conn.commit()
            print(f"updated header")
            return result.rowcount

        except Exception as e:
            print(f"Error update_header: {e}")
            return None

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

    def get_header(self, user_id, ts_id) -> Header:
        """Returns headers filtered by a given userId."""
        print(f"get_header(user_id={user_id} ts_id={ts_id})")
        query = text(
            '''SELECT 
                ts_id,
                user_id,
                amount_head,
                date_head,
                description_head,
                created_at,
                custom_rules,
                custom_categories,
                batch_name
              FROM headers WHERE user_id = :user_id AND ts_id = :ts_id ORDER BY created_at DESC''')
        result = self.conn.execute(query, {'user_id': user_id, 'ts_id': ts_id})

        row = result.fetchone()

        if row:
            return Header(ts_id=row[0], user_id=row[1], amount_head=row[2], date_head=row[3], description_head=row[4],
                          created_at=row[5], custom_rules=row[6], custom_categories=row[7], batch_name=row[8])

    def get_transactions(
        self, user_id: str, ts_id: str, page: int, limit: int, negative_only: bool = False, only_pending: bool = False, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Transaction]:
        offset = page * limit
        includePageOffset = True

        query_params = {'user_id': user_id, 'ts_id': ts_id}

        where_clauses = ["user_id = :user_id", "ts_id = :ts_id"]
        if negative_only:
            where_clauses.append("amount < 0")

        if only_pending:
            where_clauses.append("status = 'pending'")

        if start_date and start_date != 'none':
            where_clauses.append("date >= :start_date")
            query_params['start_date'] = start_date
            includePageOffset = False

        if end_date and end_date != 'none':
            where_clauses.append("date <= :end_date")
            query_params['end_date'] = end_date
            includePageOffset = False

        if includePageOffset:
            postFix = "LIMIT :limit OFFSET :offset"
            query_params['limit'] = limit
            query_params['offset'] = offset
        else:
            postFix = ""

        query_string = '''
            SELECT
                t_id,
                ts_id,
                user_id,
                date,
                description,
                amount,
                status,
                created_at,
                category
            FROM transactions 
            WHERE {} 
            ORDER BY status ASC, created_at
        '''.format(" AND ".join(where_clauses)) + postFix

        query = text(query_string)

        result = self.conn.execute(query, query_params)

        # Assuming the rows come in as a list of dictionaries
        raw = result.fetchall()

        res = []

        for row in raw:
            if negative_only:
                amount = row[5] * -1
            else:
                amount = row[5]
            res.append(Transaction(row[0], row[1], row[2], row[3],
                                   row[4], amount, row[6], row[7], row[8]))

        return res

    def get_transaction_set_aggregates(self, user_id: int, ts_id: str = None) -> List[TransactionSet]:
        """Returns transactions filtered by a given user_id and optionally by ts_id."""

        query_str = '''
            SELECT t.ts_id, COUNT(*), SUM(t.amount), MIN(h.batch_name), MIN(t.created_at) AS earliest_created_at,  MIN(t.date) as first_date, MAX(t.date) AS last_date
            FROM transactions t
            INNER JOIN headers h ON t.ts_id = h.ts_id
            WHERE t.user_id = :user_id
        '''

        # Add ts_id filtering if provided
        if ts_id is not None:
            query_str += ' AND t.ts_id = :ts_id'

        query_str += ' GROUP BY t.ts_id'

        params = {'user_id': user_id}
        if ts_id:
            params['ts_id'] = ts_id

        query = text(query_str)
        result = self.conn.execute(query, params)

        # Convert the results to a list of TransactionSet
        res = [TransactionSet(str(row[0]), row[1], row[2], row[3], row[4], row[5], row[6])
               for row in result.fetchall()]

        return res

   # ef get_transactions_to_process(self, user_id, ts_id, page, limit):
   #   """Returns transactions filtered by a given id + user_id."""
   #   print(f"get_transactions_to_process(self, {user_id}, {ts_id})")

   #   offset = page * limit
   #   query = text('''
   #       SELECT * FROM transactions
   #       WHERE user_id = :user_id AND ts_id = :ts_id AND status = 'pending'
   #       LIMIT :limit OFFSET :offset
   #   ''')
   #   result = self.conn.execute(
   #       query, {'user_id': user_id, 'ts_id': ts_id, 'limit': limit, 'offset': offset})

   #   print(
   #       f"get_transactions_to_process - Got {result.rowcount} to process for ts_id :{ts_id}")

   #   return result.fetchall()

# TODO: save category_reason + add to model
    def set_transaction_category(self, t_id, category, status):
        query = text('''
        UPDATE transactions 
        SET category = :category,
            status = :status,
            categorization_attempt = categorization_attempt + 1
        WHERE t_id = :t_id
        ''')
        result = self.conn.execute(
            query, {'category': category,  't_id': t_id, 'status': status})

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

    def get_transaction_set_by_status(self, user_id, ts_id):
        """Returns transactions filtered by a given user_id and transaction id."""
        query = text('''
            SELECT COUNT(*), status FROM transactions 
            WHERE ts_id = :ts_id
            GROUP BY status
        ''')
        result = self.conn.execute(query, {'user_id': user_id, 'ts_id': ts_id})
        return result.fetchall()

    def get_transaction_set_stats(self, user_id, ts_id, grouping):

        if grouping == 'week':
            query = text('''
                SELECT EXTRACT(WEEK FROM date) as week, COUNT(*) as num_transactions, SUM(amount) as total_amount 
                FROM transactions 
                WHERE user_id = :user_id AND ts_id = :ts_id
                GROUP BY EXTRACT(WEEK FROM date)
            ''')
        elif grouping == 'month':
            query = text('''
                SELECT EXTRACT(MONTH FROM date) as month, COUNT(*) as num_transactions, SUM(amount) as total_amount 
                FROM transactions 
                WHERE user_id = :user_id AND ts_id = :ts_id
                GROUP BY EXTRACT(MONTH FROM date)
            ''')
        # Add more grouping options as necessary
        else:
            raise ValueError("Unsupported grouping option")

        result = self.conn.execute(query, {'user_id': user_id, 'ts_id': ts_id})
        return result.fetchall()

    def delete_transaction_set(self, ts_id):
        query = text('''
            DELETE
            FROM transactions 
            WHERE ts_id = :ts_id
        ''')
        result = self.conn.execute(query, {'ts_id': ts_id})
        self.conn.commit()

        return result.rowcount

    def close(self):
        """Close the database connection."""
        # Assuming you have a session or connection object, use that to close the connection
        self.conn.close()
