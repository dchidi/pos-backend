from enum import Enum

class RoleEnum(str, Enum):
  admin = "admin"
  cashier = "cashier"
  manager = "manager"
  auditor = "auditor"
  baker = "baker"
  account = "account"
  biz_dev = "business_development"
  sales = "sales"
  mis = "management_information_system"
  supplier = "supplier"
  buyer = "buyer"
  store = "store_keeper"
  kitchen = "kitchen"
  customer_support = "customer_support"
  maintenance = "maintenance"
  hr = "human_resource"


class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"