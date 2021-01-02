from pathlib import Path


class Project:
    def __init__(self, config, root_path):
        self.documents = [Document(root_path / Path(d['file']))
                          for d in config.get('documents', [])]

    @property
    def filenames(self):
        return [d.filename for d in self.documents]


class Document:
    def __init__(self, filename):
        self.filename = filename
