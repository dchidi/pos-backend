from enum import Enum


class WarehouseType(str, Enum):
    BRANCH = "branch"
    USER = "user"  # user warehouse type cannot be shared and it requires a name.
    VENDOR = "vendor"
    FRONT_OF_HOUSE = "front_of_house"
    BACK_OF_HOUSE = "back_of_house"
    AREA = "area"
    REGION = "region"
