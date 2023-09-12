from typing import Optional
import uuid
from calendar import monthrange
from datetime import datetime
from typing import List, Tuple, Optional, NamedTuple, Dict, Any


class URLGenerator:
    def __init__(self, expanded: bool, base_url="/", page=0, limit=9999):
        self.expanded = expanded
        self.base_url = base_url
        self.page = page
        self.limit = limit

    def generate_url(self, page: int, limit: int, urlPart: str = "") -> str:
        # Ensuring that the page and limit are integers and greater than zero.
        try:
            page = max(0, int(page))
            limit = max(1, int(limit))
        except ValueError:
            raise ValueError(
                "Both 'page' and 'limit' should be positive integers.")

        # Converting the 'expanded' parameter to lowercase string representation of boolean
        expanded_str = str(self.expanded).lower()

        return f"{self.base_url}{urlPart}?page={page}&limit={limit}&expanded={expanded_str}"

    def generate_date_url(self, start_date, end_date, urlPart: str = "") -> str:
        expanded_str = str(self.expanded).lower()
        extraParams = ""
        if start_date and start_date != 'none':
            last_day_of_month = monthrange(
                start_date.year, start_date.month)[1]
            month_start_str = start_date.strftime('%Y-%m-%d')
            extraParams += f'&start_date={month_start_str}'

        if end_date and end_date != 'none':
            month_end_str = start_date.replace(
                day=last_day_of_month).strftime('%Y-%m-%d')
            extraParams += f'&end_date={month_end_str}'
        return f"{self.base_url}{urlPart}?expanded={expanded_str}{extraParams}"

    def generate_chart_url(self, type: str) -> str:
        return self.generate_url(page=0, limit=999, urlPart=f"/chart/{type}")

    def generate_next(self, total) -> str:
        page = self.page + 1

        if (page * self.limit) > total:
            return ''

        return self.generate_url(page=page, limit=self.limit)

    def generate_delete_transation(self, ts_id):
        expanded_str = str(self.expanded).lower()
        uuid_str = str(uuid.uuid4())
        if ts_id:
            return f"/tset/{ ts_id }/upload?expanded={expanded_str}"

        return f"/tset/{uuid_str}/upload?expanded={expanded_str}"

    def generate_prev(self) -> str:
        page = self.page - 1

        if (page < 1):
            return ''
        return self.generate_url(page=page, limit=self.limit)

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

    def generate_month_button_array(self, min_date: str, max_date: str) -> List[Dict[str, str]]:
        """
        Generate an array of label/urls for every month between min_date and max_date.
        Assumes min_date and max_date are in 'YYYY-MM-DD' format.
        """

        # Parsing the provided dates
        start_date = min_date
        end_date = max_date

        months = []

        # Iterate through each month between start_date and end_date
        while start_date <= end_date:

            # Forming the URL for the specific month
            url = self.generate_date_url(
                start_date=start_date, end_date=end_date)
           # url += f"&start_date={month_start_str}&end_date={month_end_str}"
            print(url)
            # Adding the month label and URL to the list
            month_label = start_date.strftime('%B %Y')
            months.append({
                "label": month_label,
                "url": url
            })

            # Moving to the next month
            if start_date.month == 12:
                start_date = start_date.replace(
                    year=start_date.year+1, month=1, day=1)
            else:
                start_date = start_date.replace(
                    month=start_date.month+1, day=1)

        return months
