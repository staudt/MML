#!/usr/bin/env python
# -*- coding: utf-8 -*-

class state:
    IDENT, TAG, ATTRIBUTES, VALUE = range(4)

with open('../samples/test.mml', 'rb') as f:
    content = f.read()

for line in iter(content.splitlines()):
    expect = state.IDENT
    parsed_line = { 'ident': '', 'tag': '', 'attributes': {}, 'value': '' }
    for c in range(len(line)):
        if line[c] == '#':
            break
        if expect == state.IDENT:
           if line[c] in [' ', '\t']:
                parsed_line['ident'] = '%s%s' % (parsed_line['ident'], line[c])
           else:
                expect = state.TAG
        if expect == state.TAG:
            if line[c] == '(':
                expect = state.ATTRIBUTES
            elif line[c] == ' ':
                expect = state.VALUE
            else:
                parsed_line['tag'] = '%s%s' % (parsed_line['tag'], line[c])
        elif expect == state.ATTRIBUTES:
            if line[c] == ')':
                expect = state.VALUE
            # not implemented yet
        elif expect == state.VALUE:
            parsed_line['value'] = '%s%s' % (parsed_line['value'], line[c])
    print parsed_line
