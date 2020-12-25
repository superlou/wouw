from docx import Document
from docx.document import Document as _Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph


class ParseState:
    START = 0


class DocxReader:
    def __init__(self, filename, id_prefix=None):
        self.filename = filename
        doc = Document(filename)
        self.requirements = self.extract_requirements(doc)
        self.id_prefix = id_prefix

    def extract_requirements(self, doc):
        state = ParseState.START

        requirements = []
        requirement = None

        for item in iter_block_items(doc):
            if state == ParseState.START:
                text = ''

                if isinstance(item, Paragraph):
                    text = item.text
                elif isinstance(item, Table):
                    text = '(table)'

                if self.is_req_start(text):
                    if requirement:
                        requirements.append(requirement)

                    requirement = Requirement()

                    ids = self.extract_ids(text)
                    if len(ids) > 0:
                        requirement.id = ids[0]

                    if len(ids) > 1:
                        requirement.trace_ids = ids[1:]

                    requirement.text = text

        if requirement:
            requirements.append(requirement)

        return requirements

    def is_req_start(self, text):
        return len(text) > 0 and text[0] == '['

    def extract_ids(self, text):
        start = text.find('[')

        if start != 0:
            return []

        finish = text.find(']')

        id_text = text[start + 1:finish]

        if id_text:
            return id_text.split(' ')
        else:
            return []

    def next_requirement_id(self):
        numbers = [r.id[len(self.id_prefix):] for r in self.requirements
                   if r.id.find(self.id_prefix) != -1]
        numbers = [int(n) for n in numbers]
        return self.id_prefix + str(max(numbers) + 1)


class Requirement:
    def __init__(self):
        self.id = None
        self.trace_ids = []
        self.text = None


def iter_block_items(parent):
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
        # print(parent_elm.xml)
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)
