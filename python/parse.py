import xml.etree.ElementTree as ET

class Element:
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
    tree = []

    def __init__(self, content):
        el = Element()
        for char in content:
            if el.state == 'find_EOL':
                if char == '\n':
                    if el.tag:
                        self._add_element(el)
                    el = Element()
            elif el.state == 'ident':
                if char in [' ', '\t']:
                    el.ident += ' ' # tabs translate to single spaces
                elif char == '#':
                    el.state = 'find_EOL'
                elif char == '\n':
                    el = Element()
                else:
                    el.state = 'tag'
                    el.tag += char
            elif el.state == 'tag':
                if char in ['\n']:
                    self._add_element(el)
                    el = Element()
                elif char == '#':
                    el.state = 'find_EOL'
                elif char in [' ', '\t']:
                    el.state = 'after_tag'
                elif char == '(':
                    el.state = 'attr'
                else:
                    el.tag += char
            elif el.state == 'after_tag':
                if char in ['\n']:
                    self._add_element(el)
                    el = Element()
                elif char == '#':
                    el.state = 'find_EOL'
                elif char == '(':
                    el.state = 'attr'
                elif char not in [' ', '\t']:
                    el.state = 'text'
                    el.text = char
            elif el.state == 'attr':
                if char in ['\n', '#']:
                    raise IndexError('")" Expected but got "%s"' % char)
                elif char == ')':
                    el.attr = self._parse_attributes(el.attr_string)
                    el.state = 'text'
                else:
                    el.attr_string += char
            elif el.state == 'text':
                if char in ['\n']:
                    self._add_element(el)
                    el = Element()
                elif char == '#':
                    el.state = 'find_EOL'
                else:
                    el.text = char if el.text == None else '%s%s' % (el.text, char)
                    if char in ['"', "'"]:
                        if el.text.strip() in ['"""', "'''"]:
                            el.state = 'text_triple_quote'
                            el.text = ''
            elif el.state == 'text_triple_quote':
                el.text = '%s%s' % (el.text, char)
                if char in ['"', "'"]:
                    if el.text.endswith('"""') or el.text.endswith("'''"):
                        el.text = el.text[:-3]
                        el.state = 'find_EOL'
        if el.tag: # if it got to EOF without saving the last one
            self._add_element(el)

    def _add_element(self, el):
        if len(self.tree)==0:
            self.tree.append(el)
            return
        bottom = self.tree[-1]
        while len(bottom.children) > 0:
            bottom = bottom.children[-1]
        if len(el.ident) == len(bottom.ident):
            if bottom.parent:
                el.parent = bottom.parent
                bottom.parent.children.append(el)
            else:
                self.tree.append(el)
            return
        elif len(el.ident) > len(bottom.ident):
            el.parent = bottom
            bottom.children.append(el)
            return
        else:
            while len(el.ident) < len(bottom.ident):
                bottom = bottom.parent
                if not bottom:
                    self.tree.append(el)
                    return
            if len(el.ident) == len(bottom.ident):
                if bottom.parent:
                    el.parent = bottom.parent
                    bottom.parent.children.append(el)
                else:
                    self.tree.append(el)
                return
        raise IndentationError('Can\t find a fit for the given identation')

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
        for el in element.children:
            self._to_xml_add(xml_el, el)

    def to_xml(self):
        if len(self.tree) == 0:
            return ''
        if len(self.tree) > 1: # XML requires a unique root, so this ups one level
            root = ET.Element('root')
            for el in self.tree:
                self._to_xml_add(root, el)
        else:
            root = ET.Element(self.tree[0].tag)
            root.text = self.tree[0].text
            root.attrib = self.tree[0].attr
            for el in self.tree[0].children:
                self._to_xml_add(root, el)
        return ET.dump(root)


with open('../test/sample.mml') as f:
    print(str(Parser(f.read()).to_xml()))
