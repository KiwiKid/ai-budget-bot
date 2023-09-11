from typing import Optional
import uuid


class URLGenerator:
    def __init__(self, expanded: bool, base_url="/", start_date: str = 'none', end_date: str = 'none'):
        self.base_url = base_url
        self.expanded = expanded
        self.start_date = start_date
        self.end_date = end_date

    def generate_url(self, page: int, limit: int) -> str:
        # Ensuring that the page and limit are integers and greater than zero.
        try:
            page = max(0, int(page))
            limit = max(1, int(limit))
        except ValueError:
            raise ValueError(
                "Both 'page' and 'limit' should be positive integers.")

        # Converting the 'expanded' parameter to lowercase string representation of boolean
        expanded_str = str(self.expanded).lower()

        extraParams = ""
        if self.start_date and self.start_date != 'none':
            extraParams += f'&start_date={self.start_date}'

        if self.end_date and self.end_date != 'none':
            extraParams += f'&end_date={self.end_date}'

        return f"{self.base_url}?page={page}&limit={limit}&expanded={expanded_str}{extraParams}"

    def generate_next(self, page, limit, total) -> str:
        page = page + 1

        if page * limit > total:
            return ''

        return self.generate_url(page, limit)

    def generate_prev(self, page, limit) -> str:
        page = page - 1

        if (page < 0):
            return ''
        return self.generate_url(page, limit)

    def generate_upload_url(self, ts_id: Optional[str] = None) -> str:

        expanded_str = str(self.expanded).lower()
        uuid_str = str(uuid.uuid4())
        if ts_id:
            return f"/tset/{ ts_id }/upload?expanded={expanded_str}"

        return f"/tset/{uuid_str}/upload?expanded={expanded_str}"

    def generate_side_bar_url(self) -> str:

        expanded_str = str(self.expanded).lower()

        return f"/sidebar?expanded={expanded_str}"

    def generate_headers_url(self, ts_id: str) -> str:

        expanded_str = str(self.expanded).lower()

        return f"/api/tset/{ts_id}/headers?expanded={expanded_str}"
