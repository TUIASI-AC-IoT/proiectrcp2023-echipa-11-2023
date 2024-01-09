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
    BLOCK_1 = 27
    BLOCK_2 = 23


class Content(IntEnum):
    TEXT_PLAIN = 0
    BYTES_STREAM = 42


class Message:
    __version = 0b01

    def __init__(self, message_type=None, message_class=None, message_code=None):
        print('\n\nmessage_manager, __init__')

        # tipul mesajului CON-00, NON-01, ACK-10, RST-11
        self.messageType = message_type

        # clasa mesajului (bitii 0-2) Request-0, Success-2, Client/Server Error Response-4/5
        self.messageClass = message_class

        # retine codul Request{GET-1.01, POST-1.02, PUT-1.03, DELETE-1.04}
        # Response{CREATED-2.01, DELETED-2.02, VALID-2.03}
        self.messageCode = message_code

        self.__options = list()
        self.__payload = bytearray()

        self.messageId = None
        self.token = None

        # nr de bytes din token (max 8)
        self.tokenLength = 0

    # Functia de encode
    def encode(self):
        print('\n\nmessage_manager, encode')
        message = bytearray()

        # Calculam lungimea tokenului (in octeti)
        if self.token:
            self.tokenLength = 0
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
            if type(value) is int:  # opaque integer (in block1 and 2)
                if value != 0:
                    value_len = value
                    while value_len > 0:
                        value_len >>= 8
                        valueLength += 1
            else:
                valueLength = len(value)

            if (option - prevOption) < 13:  # option delta < 13
                if valueLength < 13:
                    message.append(((option - prevOption) << 4) + valueLength)  # appending 1 byte
                elif valueLength < 269:
                    message.append(((option - prevOption) << 4) + 13)   # |
                    message.append(valueLength - 13)                    # |=> appending 2 bytes
                else:
                    message.append(((option - prevOption) << 4) + 14)
                    message.extend(valueLength.to_bytes(valueLength - 269, "big"))
                    # message.append(valueLength - 269)

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

            # appending the value
            if type(value) is str:
                for b in bytes(value, 'ascii'):
                    message.append(b)
            else:
                for b in value:
                    message.append(b)

        # append la payload daca exista
        if len(self.__payload) != 0:
            message.append(255)     # append la payload marker (0xFF)
            for i in self.__payload:
                message.append(i)

        return message

    def addMessageID(self, msg_id):
        print('\n\nmessage_manager, addMessageID')
        self.messageId = msg_id

    def addToken(self, token):
        print('\n\nmessage_manager, addToken')
        self.token = token

    def addOption(self, option, value):
        """option is optionNumber (0-3 opDelta, 4-7 opLength) +/- extra

        Option value not bigger than 15 bytes"""
        print('\n\nmessage_manager, addOption')
        if type(value) is int:
            val = value
            l = 0
            while val > 0:      # calculate de nr of bytes necessary to represent value
                val >>= 8
                l += 1
            value = value.to_bytes(l, "big")
        if type(value) is str:
            value = bytes(value, 'ascii')
        self.__options.append((option, value))

    def addPayload(self, content: bytearray):
        """Adds the paylaod"""
        print('\n\nmessage_manager, addPayload')
        self.__payload = content

    def displayMessage(self):
        """Displays a Message object"""
        print('\n\nmessage_manager, displayMessage')

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
        print('\n\nmessage_manager, decode')
        """Decodes the data from bytes to message object"""

        def fun(opLen, data, offset, offset2):
            if opLen < 13:  # lungime normala
                opVal = data[offset + offset2:offset + offset2 + opLen]  # getin the option Value
                offset += offset2 + opLen  # incrementing to the byte after the option
            elif opLen == 13:  # OpLen = nextByteValue + 13, celalalt byte = OpLen extended
                opLen = data[offset + offset2] + 13
                opVal = data[offset + offset2 + 1:offset + offset2 + 1 + opLen]
                offset += offset2 + 1 + opLen
            elif opLen == 14:  # OpLen are nevoie de 2 bytes(1 e full) + 4 biti in OpLen
                opLen = int.from_bytes(data[offset + offset2:offset + offset2 + 2], "big") + 269  # 255 + 14
                opVal = data[offset + offset2 + 2:offset + offset2 + 2 + opLen]
                offset += offset2 + 2 + opLen
            else:
                raise Exception("Invalid option length value!")

            return opVal, opLen, offset

        # verifica versiunea (primii 2 biti din header-primul byte adica data[0])
        if ((data[0] & 0xC0) >> 6) != self.__version:
            print(data[0] & 0xC0 >> 6)
            raise Exception("Invalid Version")

        # retine tipul mesajului CON-00, NON-01, ACK-10, RST-11
        self.messageType = (data[0] & 0x30) >> 4
        # retine token length bitii 4-7
        self.tokenLength = data[0] & 0x0F

        # 0.00 empty message
        # retine clasa mesajului (bitii 0-2) Request-0, Success-2, Client/Server Error Response-4/5
        self.messageClass = (data[1] & 0xE0) >> 5
        # retine codul Request{GET-1.01, POST-1.02, PUT-1.03, DELETE-1.04}
        # Response{CREATED-2.01, DELETED-2.02, VALID-2.03}
        self.messageCode = data[1] & 0x1F

        # retine messageID - ultimii 2 bytes din header
        self.messageId = int.from_bytes(data[2:4], "big")   # endian little/big

        # Parsing token
        if self.tokenLength == 0:
            pass
        elif self.tokenLength < 9:   # valorile de la 1001 - 1111 sunt rezervate
            self.token = 0
            for byte in data[4:4 + self.tokenLength]:    # slice-ing from index 4 to index 4+tklen
                self.token = (self.token << 8) | byte   # da append la fiecare byte din token
        else:
            raise Exception("Use of reserved token length values!")

        # Parsing Options (Check RFC7252 page 18 for details)
        if len(data) > 4 + self.tokenLength:     # verificam existenta optiunilor/payload
            index = 4 + self.tokenLength         # ducem indexul la inputul campului de optiuni
            opDeltaPrev = 0                 # setam opDelta previous pe 0
            while index < len(data):        # iteram orin optiuni
                opDelta = (data[index] & 0xF0) >> 4     # primii 4 biti din octet
                opLen = data[index] & 0x0F          # urmatorii 4 biti din octec
                if opDelta < 13:
                    opDeltaPrev += opDelta      # adunam optionDelta previous
                    opVal, opLen, index = fun(opLen, data, index, 1)
                elif opDelta == 13:     # spatiu insuficient pe 4 biti, extindem pe 1 byte din opDelta extended
                    opVal, opLen, index = fun(opLen, data, index, 2)
                elif opDelta == 14:     # sunt necesari 2 octeti pentru reprezentare (2 bytes) din Opdelta exrended
                    opDeltaPrev += int.from_bytes(data[index + 1:index + 3], "big") + 269
                    opVal, opLen, index = fun(opLen, data, index, 3)
                else:
                    if opLen == 15:     # payload marker (arata sfarsitul sectiunii de optiunui) restul mesajului se pune in payload
                        self.__payload = data[index + 1:len(data)]
                        break
                    else:
                        raise Exception("Invalid option length value!")

                self.addOption(opDeltaPrev, opVal)  # se adauga optiunea in coada de optiuni

            if index < len(data):       # se adauga restul mesajului in payload
                self.__payload = data[index + 1:len(data)]