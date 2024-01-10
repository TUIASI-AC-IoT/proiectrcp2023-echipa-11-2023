import message_manager as msm
import communication_manager as comm
import os


# Tipul mesajului va fi default de tip Confirmable
CommunicationType = msm.Type.Confirmable


class Command:

    def __init__(self):

        self.message = None

        self.Data = None

    def details(self):

        return self.message


class Create(Command):

    def __init__(self, path: list):

        super().__init__()
        self.message = msm.Message(comm.CommunicationType, msm.Class.Method, msm.Method.POST)

        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Upload(Command):

    def __init__(self, path: list, file: str):
        super().__init__()

        self.message = msm.Message(comm.CommunicationType, msm.Class.Method, msm.Method.POST)

        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)
        fileName = os.path.basename(file)

        self.message.addOption(msm.Options.URI_PATH, path)
        self.message.addOption(msm.Options.FORMAT, msm.Content.BYTES_STREAM.value)

        self.Data = file

class Rename(Command):

    def __init__(self, path, new_name: list):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.PUT)
        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)
        str = ""
        for i in new_name:
            str += i + "/"
        self.message.addPayload(bytearray(str[0:len(str)], "ascii"))



class Move(Command):

    def __init__(self, path: list, file: str):

        super().__init__()

        self.message = msm.Message(comm.CommunicationType, msm.Class.Method, msm.Method.PUT)

        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)

        self.message.addPayload(bytes(file, "ascii"))


class Download(Command):

    def __init__(self, path: list):

        super().__init__()

        self.message = msm.Message(comm.CommunicationType, msm.Class.Method, msm.Method.GET)

        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)



class ListDirectory(Command):

    def __init__(self, path: list):

        super().__init__()
        print('\nListDirectory')
        self.message = msm.Message(comm.CommunicationType, msm.Class.Method, msm.Method.GET)

        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)



class GetData(Command):

    def __init__(self, path: list):

        super().__init__()

        self.message = msm.Message(comm.CommunicationType, msm.Class.Method, msm.Method.HEAD)

        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)



class Delete(Command):

    def __init__(self, path: list):

        super().__init__()

        self.message = msm.Message(comm.CommunicationType, msm.Class.Method, msm.Method.DELETE)
        for i in path:
            self.message.addOption(msm.Options.URI_PATH, i)



