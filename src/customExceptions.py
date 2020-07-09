class DatabaseConnectionFailed(Exception):
    def __init__(self, message):
        self.message = message


class InstanceCreationFailed(Exception):
    def __init__(self, message):
        self.message = message


class StatusTransitionFailed(Exception):
    def __init__(self, message):
        self.message = message


class AuthorizationFailed(Exception):
    def __init__(self, message):
        self.message = message
