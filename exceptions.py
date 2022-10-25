class BadCredentials(Exception):

    def __init__(self, message):
        super().__init__(message)


class UnexpectedStatusCode(Exception):

    def __init__(self, method: str, endpoint: str, status_code: int, content: str):
        super().__init__(f'Got unexpected status code when performing {method} request "{endpoint}" '
                         f'to Bank of Georgia with status code {status_code}. response content: {content}')
