


class FormatError(ValueError):
    def __init__(self, line, file):
        self.line = line
        self.file = file