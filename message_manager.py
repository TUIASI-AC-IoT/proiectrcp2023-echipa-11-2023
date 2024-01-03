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


class ServerError(Code):
    InternalServerError = 0
    NotImplemented = 1
    BadGateway = 2
    ServiceUnavailable = 3
    GatewayTimeout = 4


class Options(IntEnum):
    LOCATION_PATH = 8
    URI_PATH = 11
    FORMAT = 12
    ACCEPT = 17
    BLOCK_1 = 23
    BLOCK_2 = 27


class Content(IntEnum):
    TEXT_PLAIN = 0
    BYTES_STREAM = 42


class Message:
    __version = 0b01

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
        if self.token:
            tokenLen = self.token
            print(tokenLen)
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

    def addMessageID(self, msg_id):
        self.messageId = msg_id

    def addToken(self, token):
        self.token = token

    def addOption(self, option, value):
        """option is optionNumber (0-3 opDelta, 4-7 opLength) +/- extra

        Option value not bigger than 15 bytes"""
        self.__options.append((option, value))

    def addPayload(self, content: bytearray):
        self.__payload = content

    def displayMessage(self):
        print('-----------------------------\n\t\tHeader')
        print('Byte1:\n\tVersion: ', self.__version, end='\n\t')
        print('Type: ', self.messageType, end='\n\t')
        print('Token Len: ', self.tokenLength)
        print('Byte2:\n\tCode: ', self.messageCode)
        print('Byte3-4:\n\tMessageID: ', self.messageId, end='\n-----------------------------\n')
        print('Token: ', self.token, end='\n-----------------------------\n')
        print('Options: ', self.__options, end='\n-----------------------------\n')
        print('Payload: ', self.__payload, end='\n-----------------------------\n')

    # Decodarea mesajului primit
    def decode(self, data: bytearray):
        if (data[0] & 0xC0) >> 6 != self.__version:
            print(data[0] & 0xC0 >> 6)
            raise Exception("Invalid version")

        self.messageType = (data[0] & 0x30) >> 4
        self.tokenLength = data[0] & 0x0F

        self.messageClass = (data[1] & 0xE0) >> 5
        self.messageCode = data[1] & 0x1F

        self.messageId = int.from_bytes(data[2:4], "big")
        self.token = int.from_bytes(data[8:12], "big")

