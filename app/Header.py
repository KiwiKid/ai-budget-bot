class Header:
    def __init__(self,
                 ts_id,
                 user_id,
                 amount_head,
                 date_head,
                 description_head,
                 created_at,
                 custom_rules=None,
                 custom_categories=None):

        self.ts_id = ts_id
        self.user_id = user_id
        self.amount_head = amount_head.split('|')
        self.date_head = date_head.split('|')
        self.description_head = description_head.split('|')
        self.created_at = created_at
        self.custom_rules = custom_rules.split('|') if custom_rules else []
        self.custom_categories = custom_categories.split(
            '|') if custom_categories else []
