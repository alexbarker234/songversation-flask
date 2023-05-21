# Spotify

class UnauthorisedException(Exception):
    "Raised when user is not authorised"
    pass

# User

class UserNotFoundException(Exception):
    "Raised when a user is not found"

class InvalidFriendException(Exception):
    "Raised when a user tries to add an invalid user as friend"
