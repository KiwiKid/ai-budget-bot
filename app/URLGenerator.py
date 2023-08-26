from typing import Optional
import uuid


class URLGenerator:
    def __init__(self, expanded: bool, base_url="/"):
        self.base_url = base_url
        self.expanded = expanded

    def generate_url(self, page: int, limit: int, expanded: bool) -> str:
        # Ensuring that the page and limit are integers and greater than zero.
        try:
            page = max(0, int(page))
            limit = max(1, int(limit))
        except ValueError:
            raise ValueError(
                "Both 'page' and 'limit' should be positive integers.")

        # Converting the 'expanded' parameter to lowercase string representation of boolean
        expanded_str = str(expanded).lower()

        return f"{self.base_url}?page={page}&limit={limit}&expanded={expanded_str}"

    def generate_next(self, page, limit, total, expanded) -> str:
        page = page + 1

        if page * limit > total:
            return ''

        return self.generate_url(page, limit, expanded)

    def generate_prev(self, page, limit, expanded) -> str:
        page = page - 1

        if (page < 0):
            return ''
        return self.generate_url(page, limit, expanded)

    def generate_upload_url(expanded: bool, ts_id: Optional[str] = None) -> str:

        expanded_str = str(expanded).lower()
        uuid_str = str(uuid.uuid4())
        if ts_id:
            return f"/tset/{ ts_id }/upload?expanded={expanded_str}"

        return f"/tset/{uuid_str}/upload?expanded={expanded_str}"

    def generate_side_bar_url(expanded) -> str:

        expanded_str = str(expanded).lower()

        return f"/sidebar?expanded={expanded_str}"
