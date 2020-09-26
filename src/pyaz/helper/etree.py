from lxml import etree
from collections.abc import Iterable

def append_to_element(root, doc, item_tag='item'):
    if isinstance(doc, dict):
        for attr in doc:
            el = etree.Element(attr)
            root.append(el)
            append_to_element(el, doc[attr])
    elif isinstance(doc, str):
        root.text = doc
    elif isinstance(doc, Iterable):
        for item in doc:
            el = etree.Element(item_tag)
            root.append(el)
            append_to_element(el, item)
    else:
        root.text = str(doc)
    return root

def as_etree(doc, root_tag='root', item_tag='item'):
    if etree.iselement(doc):
        return doc
    tree = etree.Element(root_tag)
    return append_to_element(tree, doc, item_tag)

def as_table(doc, path_item, field_map:dict, header_row=False, path_root='/', output_fields=None):
    def _map_field(item, xpath):
        result = ''
        for match in item.xpath(xpath):
            result += match.text
        return result

    if not output_fields:
        output_fields = tuple(field_map.keys())
    if header_row:
        yield tuple(output_fields)
    for root in doc.xpath(path_root):
        for item in root.xpath(path_item):
            row = tuple(_map_field(item, field_map[field_name]) for field_name in output_fields)
            yield row

    pass

__all__ = ['as_etree']
