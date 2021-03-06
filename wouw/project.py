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
        dr = DocxReader(self.path, self.id_prefix)
        self.requirements = dr.extract_requirements()
        self.warnings = self.check_for_duplicate_ids()

    def next_requirement_id(self):
        numbers = [r.id[len(self.id_prefix):] for r in self.requirements
                   if r.id.find(self.id_prefix) != -1]
        numbers = [int(n) for n in numbers]

        if len(numbers) > 0:
            return self.id_prefix + str(max(numbers) + 1)
        else:
            return self.id_prefix + str(1)

    def check_for_duplicate_ids(self):
        ids = [requirement.id for requirement in self.requirements]
        duplicates = sorted(list_duplicates(ids))
        warnings = [f'Duplicate requirement ID: "{id}"'
                    for id in duplicates]

        return warnings


def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set(x for x in seq if x in seen or seen_add(x))
    # turn the set into a list (as requested)
    return list(seen_twice)
