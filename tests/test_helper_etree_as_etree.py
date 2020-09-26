from unittest import mock
import pytest
from lxml import etree
from pyaz.helper.etree import as_etree, append_to_element

def test_should_return_same_doc_when_etree_passed():
    doc = etree.Element('root')
    assert doc is as_etree(doc)

def test_should_return_tree_with_given_root_tag():
    tree = as_etree('doc', root_tag='mydoc')
    assert 'mydoc' == tree.tag

def test_should_retrun_result_from_call_to_append_to_element():
    expected = '__xx__'
    with mock.patch('pyaz.helper.etree.append_to_element') as append_to_etree_mock:
        append_to_etree_mock.return_value = expected
        result = as_etree('Hello world')
        assert expected is result

def test_append_to_element_returns_same_tree_object():
    tree = etree.Element('root')
    result = append_to_element(tree, 'Str')
    assert tree is result

def test_append_to_element_sets_text_given_doc_is_string():
    tree = etree.Element('root')
    result = append_to_element(tree, 'Hello Bilbo')
    assert 'Hello Bilbo' == result.text


def test_append_to_element_sets_text_converted_to_str_given_doc_is_int():
    tree = etree.Element('root')
    result = append_to_element(tree, 23)
    assert '23' == result.text

def test_append_to_element_appends_dictionary_elements_to_tree():
    tree = etree.Element('root')
    data = dict(name='John', age=7320)
    result = append_to_element(tree, data)
    assert b'<root><name>John</name><age>7320</age></root>'  == etree.tostring(result)

def test_append_to_element_appends_list_elements_to_tree():
    tree = etree.Element('root')
    data = ['John', 'Jane']
    result = append_to_element(tree, data, item_tag='user')
    assert b'<root><user>John</user><user>Jane</user></root>'  == etree.tostring(result)
