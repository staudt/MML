# -*- coding: utf-8 -*-
""" MML Python Parser """

import xml.etree.ElementTree as ET

class Element:
    """Represents a MML Element"""
    def __init__(self):
        self.ident = ''
        self.tag = ''
        self.attr_string = ''
        self.attr = None
        self.text = None
        self.state = 'ident'
        self.children = []
        self.parent = None

class Parser:
    """Parses a MML document and allows conversion to other formats"""
    def __init__(self, content):
        self.tree = []
        element = Element()
        for char in content:
            if element.state == 'find_EOL':
                if char == '\n':
                    if element.tag:
                        self._add_element(element)
                    element = Element()
            elif element.state == 'ident':
                if char in [' ', '\t']:
                    element.ident += ' ' # tabs translate to single spaces
                elif char == '#':
                    element.state = 'find_EOL'
                elif char == '\n':
                    element = Element()
                else:
                    element.state = 'tag'
                    element.tag += char
            elif element.state == 'tag':
                if char in ['\n']:
                    self._add_element(element)
                    element = Element()
                elif char == '#':
                    element.state = 'find_EOL'
                elif char in [' ', '\t']:
                    element.state = 'after_tag'
                elif char == '(':
                    element.state = 'attr'
                else:
                    element.tag += char
            elif element.state == 'after_tag':
                if char in ['\n']:
                    self._add_element(element)
                    element = Element()
                elif char == '#':
                    element.state = 'find_EOL'
                elif char == '(':
                    element.state = 'attr'
                elif char not in [' ', '\t']:
                    element.state = 'text'
                    element.text = char
            elif element.state == 'attr':
                if char in ['\n', '#']:
                    raise IndexError('")" Expected but got "%s"' % char)
                elif char == ')':
                    element.attr = self._parse_attributes(element.attr_string)
                    element.state = 'text'
                else:
                    element.attr_string += char
            elif element.state == 'text':
                if char in ['\n']:
                    self._add_element(element)
                    element = Element()
                elif char == '#':
                    element.state = 'find_EOL'
                else:
                    element.text = char if element.text is None else '%s%s' % (element.text, char)
                    if char in ['"', "'"]:
                        if element.text.strip() in ['"""', "'''"]:
                            element.state = 'text_triple_quote'
                            element.text = ''
            elif element.state == 'text_triple_quote':
                element.text = '%s%s' % (element.text, char)
                if char in ['"', "'"]:
                    if element.text.endswith('"""') or element.text.endswith("'''"):
                        element.text = element.text[:-3]
                        element.state = 'find_EOL'
        if element.tag: # if it got to EOF without saving the last one
            self._add_element(element)

    def _add_element(self, element):
        if not self.tree:
            self.tree.append(element)
            return
        bottom = self.tree[-1]
        while bottom.children:
            bottom = bottom.children[-1]
        if len(element.ident) == len(bottom.ident):
            if bottom.parent:
                element.parent = bottom.parent
                bottom.parent.children.append(element)
            else:
                self.tree.append(element)
            return
        elif len(element.ident) > len(bottom.ident):
            element.parent = bottom
            bottom.children.append(element)
            return
        else:
            while len(element.ident) < len(bottom.ident):
                bottom = bottom.parent
                if not bottom:
                    self.tree.append(element)
                    return
            if len(element.ident) == len(bottom.ident):
                if bottom.parent:
                    element.parent = bottom.parent
                    bottom.parent.children.append(element)
                else:
                    self.tree.append(element)
                return
        raise IndentationError('Can\'t find a fit for the given identation')

    def _parse_attributes(self, attr_string):
        attr = {}
        state = 'name'
        name, value = '', None
        for char in attr_string:
            if state == 'name':
                if char in ['=']:
                    if not name:
                        raise IndexError('"=" found when expecting attribute name')
                    state = 'value'
                elif char == ',':
                    attr[name] = value
                    name, value = '', None
                else:
                    name += char
            elif state == 'value':
                if char == ',':
                    attr[name] = value
                    name, value = '', None
                    state = 'name'
                elif not value and char in ['"', "'"]:
                    state = 'value_quoted'
                else:
                    value = char if not value else '%s%s' % (value, char)
            elif state == 'value_quoted':
                if char in ['"', "'"]:
                    attr[name] = value
                    name, value = '', None
                    state = 'wait_comma'
                else:
                    value = char if not value else '%s%s' % (value, char)
            elif state == 'wait_comma':
                if char == ',':
                    state = name
                elif char != ' ':
                    raise IndexError('Expected " " or "," but got "%s"' % char)
        if name:
            attr[name] = value
        return attr

    def _to_xml_add(self, parent, element):
        xml_el = ET.SubElement(parent, element.tag)
        xml_el.text = element.text
        xml_el.attrib = element.attr
        for sub_element in element.children:
            self._to_xml_add(xml_el, sub_element)

    def to_xml(self):
        """Returns a XML-friendly string representation of the data"""
        if not self.tree:
            return ''
        if len(self.tree) > 1: # XML requires a unique root, so this ups one level
            root = ET.Element('root')
            for element in self.tree:
                self._to_xml_add(root, element)
        else:
            root = ET.Element(self.tree[0].tag)
            root.text = self.tree[0].text
            root.attrib = self.tree[0].attr
            for element in self.tree[0].children:
                self._to_xml_add(root, element)
        return ET.dump(root)


with open('../test/sample.mml') as f:
    print(str(Parser(f.read()).to_xml()))
