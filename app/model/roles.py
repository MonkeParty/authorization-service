from enum import Enum

class Role(Enum):
    anonymous = 'anonymous'
    user = 'user'
    paid_user = 'paid-user'
    admin = 'admin'