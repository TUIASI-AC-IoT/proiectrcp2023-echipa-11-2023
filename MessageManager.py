from enum import IntEnum


class Type(IntEnum):
    Confirmable = b'00'
    NonConfirmable = b'01'
    Acknowledgement = b'10'
    Reset = b'11'


class Class(IntEnum):
    Method = 0
    Success = 2
    Client_Error = 4
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


class ClientError(Code):
    Bad_Request = 0
    Bad_Option = 2
    Not_Found = 4
    Method_Not_Allowed = 5
    Not_Acceptable = 6


class Message:
    __version = 1

    def __init__(self, message_type=None, message_class=None, message_code=None):
        self.messageType = message_type
        self.messageClass = message_class
        self.messageCode = message_code
        self.__options = list()
        self.__payload = bytearray()

        self.messageId = None
        self.token = None
        self.tokenLength = 0

    # Functia de encode
    def encode(self):

        message = bytearray()

        # Calculam lungimea tokenului
        if self.token != 0:
            tokenLen = self.token
            while tokenLen > 0 and self.tokenLength <= 8:
                tokenLen >>= 8
                self.tokenLength += 1

        message.append(((self.__version << 6) + (self.messageType << 4) + self.tokenLength))
        message.append((self.messageClass << 5) + self.messageCode)
        message.extend(self.messageId.to_bytes(2, 'big'))
        message.extend(self.token.to_bytes(self.tokenLength, 'big'))

        # Append la bitii de optiune
        prevOption = 0
        for (option, value) in self.__options:
            valueLength = 0
            # print(type(val.value))
            if type(value) is int:
                if value != 0:
                    value_len = value
                    while value_len > 0:
                        value_len >>= 8
                        valueLength += 1
            else:
                valueLength = len(value)

            if (option - prevOption) < 13:
                if valueLength < 13:
                    message.append(((option - prevOption) << 4) + valueLength)
                elif valueLength < 269:
                    message.append(((option - prevOption) << 4) + 13)
                    message.append(valueLength - 13)
                else:
                    message.append(((option - prevOption) << 4) + 14)
                    message.append(valueLength - 269)

                prevOption = option
            else:
                if valueLength < 13:
                    message.append((13 << 4) + valueLength)
                    message.append(option - prevOption - 13)
                elif valueLength < 269:
                    message.append((13 << 4) + 13)
                    message.append(option - prevOption - 13)
                    message.append(valueLength - 13)
                else:
                    message.append((13 << 4) + 14)
                    message.append(option - prevOption - 13)
                    message.append(valueLength - 269)

                prevOption = option

        # append la payload daca exista
        if len(self.__payload) != 0:
            message.append(255)
            for i in self.__payload:
                message.append(i)

        return message
