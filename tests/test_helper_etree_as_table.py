from unittest import mock
import pytest
from lxml import etree
from pyaz.helper.etree import as_table

@pytest.fixture(scope="session")
def fix_book_tree():
    doc_xml = """
       <books>
          <book><title>Gone</title></book>
          <book><title>Winds</title><id>5</id></book>
        </books>
    """
    yield etree.fromstring(doc_xml)

@pytest.fixture(scope="session")
def fix_book_map():
    return dict(id='id',
                 title='title')

def test_should_return_generator_of_mapped_tuples(fix_book_tree, fix_book_map):
    expected = [('','Gone',), ('5','Winds')]
    result = as_table(fix_book_tree, path_item='book', field_map=fix_book_map,
                      path_root='/books' )
    assert expected == list(result)

def test_should_return_head_row(fix_book_tree, fix_book_map):
    expected = ('id','title')
    result = as_table(fix_book_tree, path_item='book', field_map=fix_book_map,
                      path_root='/books', header_row=True )
    assert expected == list(result)[0]



