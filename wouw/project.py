from pathlib import Path
from .docx_reader import DocxReader


class Project:
    def __init__(self, config, root_path):
        self.documents = [Document(root_path / Path(d['file']), d['id_prefix'])
                          for d in config.get('documents', [])]

    @property
    def paths(self):
        return [d.path for d in self.documents]

    def get_document_by_path(self, path):
        matches = [d for d in self.documents if d.path == path]

        if len(matches) == 0:
            raise Exception('No matches found')
        elif len(matches) > 1:
            raise Exception('Multiple documents with same path found')

        return matches[0]


class Document:
    def __init__(self, path, id_prefix):
        self.path = path
        self.id_prefix = id_prefix
        self.dr = DocxReader(path, id_prefix)
        self.refresh()

    def refresh(self):
        self.dr = DocxReader(self.path, self.id_prefix)
