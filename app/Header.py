from typing import List, Optional, Union
from datetime import datetime
from app.utils import pg_array_to_python_list


class Header:
    def __init__(self,
                 ts_id: str,
                 batch_name: str,
                 is_published: bool,
                 user_id: str,
                 amount_head: Optional[str],
                 date_head: Optional[str],
                 description_head: Optional[str],
                 # Based on your information, I'm not sure of the exact type of created_at, you might need to adjust.
                 created_at: Union[str, datetime],
                 custom_rules: Optional[str] = None,
                 custom_categories: Optional[str] = None,
                 ) -> None:

        if custom_categories == None or len(custom_categories) == 0 or custom_categories[0] == '':
            self.custom_categories = [
                'Housing',
                'Groceries',
                'Eating Out',
                'Transportation',
                'Healthcare',
                'Entertainment',
                'Apparel',
                'Income',
                'Debts'
            ]
        else:
            self.custom_categories = pg_array_to_python_list(custom_categories)

        self.ts_id = ts_id
        self.user_id = user_id
        self.amount_head = amount_head
        self.date_head = date_head
        self.description_head = pg_array_to_python_list(description_head)
        self.created_at = created_at
        self.custom_rules = custom_rules
        self.batch_name = batch_name
        self.is_published = is_published
