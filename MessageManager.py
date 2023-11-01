from enum import IntEnum

class Type(IntEnum):
    Confirmable = b'00'
    NonConfirmable = b'01'
    Acknowledgement = b'10'
    Reset = b'11'


class Class(IntEnum):
    Method = 0
    Success = 2
    Cleint_Error = 4
    Server_Error = 5

class Code(IntEnum):
    pass

class Method(Code):
    EMPTY = 0
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
    HEAD = 8

class Success(Code):
    Created = 1
    Deleted = 2
    Valid = 3
    Content = 5


class Client_Error(Code):
    Bad_Request = 0
    Bad_Option = 2
    Not_Found = 4
    Method_Not_Allowed = 5
    Not_Acceptable = 6

