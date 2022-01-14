""" Set of exceptions related to domain errors """


class DomainError(Exception):
    """Generic exception thrown by the domain on business logic errors"""

    def __init__(self, message, **details):
        self.message = message
        self.details = details
