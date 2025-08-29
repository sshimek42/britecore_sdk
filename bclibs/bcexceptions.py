class NoDataReturned(Exception):
    def __init__(self, message, request=None, http_error=None):
        self.message = message
        self.request = request
        self.http_error = http_error
        super().__init__(self.message)

    def __str__(self):
        return (f"BriteCore was unable to return any data - {self.message}\n"
                f"Request: {self.request}\n"
                f"HTTP Error: {self.http_error}")