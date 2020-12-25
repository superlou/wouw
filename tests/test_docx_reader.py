from wouw import DocxReader


def test_docx_reader_has_filename():
    dr = DocxReader('tests/data/test.docx')
    assert dr.filename == 'tests/data/test.docx'
