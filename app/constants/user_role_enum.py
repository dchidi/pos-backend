from enum import Enum


# Only two roles is held here for new user initialization. 
# Organization will define their own roles and grant permissions to them as desired
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    CASHIER = "cashier"
