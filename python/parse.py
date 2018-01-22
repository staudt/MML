
class Line:
    def __init__(self):
        self.ident = ''
        self.tag = ''
        self.attr_string = ''
        self.attr = None
        self.value = None
        self.state = 'ident'
        self.children = []
        self.parent = None

class Parser:
    code = []

    def parse(self, content):
        self.get_lines(content)

    def add_line(self, line):
        if len(self.code)==0:
            self.code.append(line)
            return
        bottom = self.code[-1]
        while len(bottom.children) > 0:
            bottom = bottom.children[-1]
        if len(line.ident) == len(bottom.ident):
            if bottom.parent:
                line.parent = bottom.parent
                bottom.parent.children.append(line)
            else:
                self.code.append(line)
            return
        elif len(line.ident) > len(bottom.ident):
            line.parent = bottom
            bottom.children.append(line)
            return
        else:
            while len(line.ident) < len(bottom.ident):
                bottom = bottom.parent
                if not bottom:
                    self.code.append(line)
                    return
            if len(line.ident) == len(bottom.ident):
                if bottom.parent:
                    line.parent = bottom.parent
                    bottom.parent.children.append(line)
                else:
                    self.code.append(line)
                return
        raise IndentationError('Can\t find a fit for the given identation')


    def get_lines(self, content):
        line = Line()
        for char in content:
            if line.state == 'find_EOL':
                if char == '\n':
                    if line.tag:
                        self.add_line(line)
                    line = Line()
            elif line.state == 'ident':
                if char in [' ', '\t']:
                    line.ident += ' ' # tabs translate to single spaces
                elif char == '#':
                    line.state = 'find_EOL'
                elif char == '\n':
                    line = Line()
                else:
                    line.state = 'tag'
                    line.tag += char
            elif line.state == 'tag':
                if char in ['\n']:
                    self.add_line(line)
                    line = Line()
                elif char == '#':
                    line.state = 'find_EOL'
                elif char in [' ', '\t']:
                    line.state = 'after_tag'
                elif char == '(':
                    line.state = 'attr'
                else:
                    line.tag += char
            elif line.state == 'after_tag':
                if char in ['\n']:
                    self.add_line(line)
                    line = Line()
                elif char == '#':
                    line.state = 'find_EOL'
                elif char == '(':
                    line.state = 'attr'
                elif char not in [' ', '\t']:
                    line.state = 'value'
                    line.value = char
            elif line.state == 'attr':
                if char in ['\n', '#']:
                    raise IndexError('")" Expected but got "%s"' % char)
                elif char == ')':
                    line.attr = self.parse_attributes(line.attr_string)
                    line.state = 'value'
                else:
                    line.attr_string += char
            elif line.state == 'value':
                if char in ['\n']:
                    self.add_line(line)
                    line = Line()
                elif char == '#':
                    line.state = 'find_EOL'
                else:
                    line.value = char if line.value == None else '%s%s' % (line.value, char)
                    if char in ['"', "'"]:
                        if line.value.strip() in ['"""', "'''"]:
                            line.state = 'value_triple_quote'
                            line.value = ''
            elif line.state == 'value_triple_quote':
                line.value = '%s%s' % (line.value, char)
                if char in ['"', "'"]:
                    if line.value.endswith('"""') or line.value.endswith("'''"):
                        line.value = line.value[:-3]
                        line.state = 'find_EOL'
        if line.tag: # if it got to EOF without saving the last one
            self.add_line(line)
        return True

    def parse_attributes(self, attr_string):
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
                    state == 'wait_comma'
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


with open('../test/sample.mml') as f:
    Parser().parse(f.read())
