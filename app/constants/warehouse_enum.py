from enum import Enum

class WarehouseType(str, Enum):
    BRANCH = "branch"
    USER = "user"
    VENDOR = "vendor"
    FRONT_OF_HOUSE = "front_of_house"
    BACK_OF_HOUSE = "back_of_house" # If they are running shift, then the best type to use is USER
    AREA = "area"
    REGION ="region"