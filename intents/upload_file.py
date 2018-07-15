from intents.base import UploadFile

class IntentUploadFile(UploadFile):
    NAME = 'UPLOAD_FILE'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        return self.Response()
