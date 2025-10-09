from enum import Enum


class OperationType(Enum):
    BORROW = "BORROW"
    RETURN = "RETURN"
    EXTEND = "EXTEND"