from intents.base import UploadFile

class IntentUploadFile2(UploadFile):
    NAME = 'UPLOAD_FILE2'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        return self.Response()
