#!/usr/bin/env python
# -*- coding: utf-8 -*-

class state:
    IDENTATION, TAG, ATTRIBUTES, VALUE = range(4)

with open('../samples/test.mml', 'rb') as f:
    content = f.read()

for line in iter(content.splitlines()):
    expect = state.IDENTATION
    parsed_line = { 'ident': '', 'tag': '', 'attributes': {}, 'value': '', 'children': [] }
    for c in range(len(line)):
        if expect == state.IDENTATION:
           if line[c] == '#':
                break
           if line[c] in [' ', '\t']:
                parsed_line['ident'] = '%s%s' % (parsed_line['ident'], line[c])
           else:
                expect = state.TAG
        if expect == state.TAG:
            if line[c] == '#':
                break
            if line[c] == '(':
                expect = state.ATTRIBUTES
            elif line[c] == ' ':
                expect = state.VALUE
            else:
                parsed_line['tag'] = '%s%s' % (parsed_line['tag'], line[c])
        elif expect == state.ATTRIBUTES:
            if line[c] == '#':
                #fail
                pass
            if line[c] == ')':
                expect = state.VALUE
            else:
                pass
                # attr parse not yet implemented implemented yet
        elif expect == state.VALUE:
            if line[c] == '#':
                break
            parsed_line['value'] = '%s%s' % (parsed_line['value'], line[c])
    print parsed_line
