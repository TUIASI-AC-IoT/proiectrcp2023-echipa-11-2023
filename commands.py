import message_manager as msm

# Tipul mesajului va fi default de tip Confirmable
CommunicationType = msm.Type.Confirmable


class Command:

    def __init__(self):

        self.message = None

    def details(self):

        return self.message


class Create(Command):

    def __init__(self, path):

        super().__init__()
        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.POST)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Upload(Command):

    def __init__(self, path, file):
        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.POST)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Rename(Command):

    def __init__(self, path, new_name):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.PUT)

        self.message.addOption(msm.Options.LOCATION_PATH, path)

        self.message.addPayload(bytearray(new_name, 'ascii'))


class Move(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.PUT)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Download(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.GET)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class ListDirectory(Command):

    def __init__(self, path):

        super().__init__()
        print('\nListDirectory')
        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.GET)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class GetData(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.HEAD)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Delete(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.DELETE)

        self.message.addOption(msm.Options.LOCATION_PATH, path)

