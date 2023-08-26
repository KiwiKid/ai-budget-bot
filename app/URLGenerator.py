class URLGenerator:
    def __init__(self, base_url="/"):
        self.base_url = base_url

    def generate_url(self, page: int, limit: int, expanded: bool):
        # Ensuring that the page and limit are integers and greater than zero.
        try:
            page = max(1, int(page))
            limit = max(1, int(limit))
        except ValueError:
            raise ValueError(
                "Both 'page' and 'limit' should be positive integers.")

        # Converting the 'expanded' parameter to lowercase string representation of boolean
        expanded_str = str(expanded).lower()

        return f"{self.base_url}?page={page}&limit={limit}&expanded={expanded_str}"

    def generate_next(self, page, limit, expanded):
        page = page + 1

        return self.generate_url(page, limit, expanded)

    def generate_prev(self, page, limit, expanded):
        page = page - 1

        return self.generate_url(page, limit, expanded)
