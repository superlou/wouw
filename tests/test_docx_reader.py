from wouw import DocxReader


def test_docx_reader_has_filename():
    dr = DocxReader('tests/data/test.docx')
    assert dr.filename == 'tests/data/test.docx'


def test_docx_reader_reads_requirements():
    dr = DocxReader('tests/data/test.docx')
    assert len(dr.requirements) == 6
    assert [r.id for r in dr.requirements] == ['r1', 'r2', 'r3',
                                               'r4', 'r5', 'r6']
    assert [r.trace_ids for r in dr.requirements] == [
        [], [], [], [], ['axp-0003'], ['axp-1421', 'axp-17']
    ]


def test_extract_ids():
    dr = DocxReader('tests/data/test.docx')
    assert dr.extract_ids('[a1234] text') == ['a1234']
    assert dr.extract_ids('[a1234 b421] text') == ['a1234', 'b421']
