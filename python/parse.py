#!/usr/bin/env python
# -*- coding: utf-8 -*-

class state:
    IDENT, TAG, ATTR_NAME, ATTR_VALUE, VALUE = range(5)
SPACES = (' ', '\t')
QUOTES = ('"', '\'')

class ParseException(Exception):  # TODO: get line and col
    pass

with open('../samples/test.mml', 'rb') as f:
    content = f.read()

for line in iter(content.splitlines()):
    line = line.decode('utf-8')
    print(line)
    expect = state.IDENT
    attr_name, attr_value, attr_quoted = None, None, False
    tag = { 'ident': '', 'name': '', 'attributes': {}, 'value': None, 'children': [] }
    for c in range(len(line)):
        if line[c] == '#':
            break
        if expect == state.IDENT:
           if line[c] in SPACES:
                tag['ident'] = '%s%s' % (tag['ident'], line[c])
           else:
                expect = state.TAG
        if expect == state.TAG:
            if line[c] == '(':
                expect = state.ATTR_NAME
            elif line[c] == ' ':
                expect = state.VALUE
            else:
                tag['name'] = '%s%s' % (tag['name'], line[c])
        elif expect == state.ATTR_NAME:
            if line[c] == ')':
                if attr_name:
                    tag['attributes'][attr_name] = ''
                expect = state.VALUE
            elif line[c] in SPACES:
                tag['attributes'][attr_name] = ''
                attr_name, attr_value, attr_quoted = None, None, False
            elif line[c] == '=':
                if not attr_name:
                    raise ParseException('Unexpected "="')
                expect = state.ATTR_VALUE
            else:
                if not attr_name:
                    if line[c] not in SPACES:
                        attr_name = line[c]
                else:
                    if line[c] in SPACES:
                        raise ParseException('Unexpected space in attribute name')
                    attr_name = '%s%s' % (attr_name if attr_name else '', line[c])
        elif expect == state.ATTR_VALUE:
            if attr_value is None:
                if line[c] in SPACES:
                    raise ParseException('Unexpected space in attribute name')
                if line[c] in QUOTES:
                    attr_quoted, attr_value = True, ''
                else:
                    attr_value = line[c]
            else:
                if attr_quoted:
                    if line[c] in QUOTES:
                        tag['attributes'][attr_name] = attr_value
                        attr_name, attr_value, attr_quoted = None, None, False
                        expect = state.ATTR_NAME
                    else:
                        attr_value = '%s%s' % (attr_value, line[c])
                else:
                    if line[c] == ')':
                       tag['attributes'][attr_name] = attr_value
                       expect = state.VALUE
                    if line[c] in QUOTES:
                        ParseException('Unexpected character inside attribute value')
                    if line[c] in SPACES:
                        if len(attr_value)==0:
                            ParseException('Unexpected space in attribute value')
                        else:
                            tag['attributes'][attr_name] = attr_value
                            attr_name, attr_value, attr_quoted = None, None, False
                            expect = state.ATTR_NAME
                    else:
                        attr_value = '%s%s' % (attr_value, line[c])
        elif expect == state.VALUE:
            if tag['value'] is None:
                tag['value'] = ''
            tag['value'] = '%s%s' % (tag['value'], line[c])
    print(tag)
    print('')
    if expect in (state.ATTR_NAME, state.ATTR_VALUE):
        raise ParseException('Unexpected break when parsing attributes')
