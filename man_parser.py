from recordclass import recordclass

import re


main_titles = ['NAME', 'SYNOPSIS', 'DESCRIPTION', 'OPTIONS', '']
KEY_LINE_LENGTH = 5
INDENT = '  '
FIRST_BIG_SPACE = 25


class ManParser:
    def __init__(self, filename):
        self.filename = filename

        self.Layout = recordclass('Layout', 'title descr')
        self.Key = recordclass('Key', 'name descr')
        self.KeyName = recordclass('KeyName', 'name arg')

        self.one_key = re.compile(r'(-[a-zA-Z]+) ')
        self.word_key = re.compile(r'(--[a-zA-Z-]+)(=\w+)?')
        self.url = re.compile(r'http[s]?://(?:[a-zA-Z0-9$-_@.&+!*\(\),]|'
                               '(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def parse(self):
        layouts = self.get_layouts()
        for title, descr in layouts:
            if title in ['OPTIONS', 'DESCRIPTION']:
                self.parse_layout_description(title, descr)

    def parse_layout_description(self, title, descr):
        keys = []

        lines = iter(descr)
        index = -1
        for line in lines:
            index += 1
            indent, line = self.remove_spaces(line)

            if self.is_correct_key(line, descr, index):
                index = self.handle_key(indent, line, index,
                                        descr, lines, keys)
        for key in keys:
            print('KEY: %s' % key, end='\n\n')

    def get_name_description(self, words):
        global KEY_LINE_LENGTH

        return (' '.join(words), []) if len(words) < KEY_LINE_LENGTH else \
               (' '.join(words[:2]), [' '.join(filter(None, words[2:]))])

    def add_key(self, key, key_list, outer_key):
        if outer_key is None or len(outer_key) == 0:
            key_list.append(key)
        else:
            outer_key[-1].descr.append(key)

    def get_outer_key(self, outer_key, key):
        new_outer_key = []
        if outer_key is not None:
            for o_key in outer_key:
                new_outer_key.append(o_key)
        new_outer_key.append(key)
        return tuple(new_outer_key)

    def handle_key(self, indent, line, index, descr, lines,
                   key_list, outer_key=None):
        text = ''
        name, description = self.get_name_description(line.split(' '))
        name = name.strip()
        key = self.Key(name=name, descr=description)
        while True:
            try:
                ind, des = self.remove_spaces(next(lines))
            except StopIteration:
                self.add_key(key, key_list, outer_key)
                return index
            index += 1
            if ind <= indent and des != '\n':
                break
            if self.is_correct_key(des, descr, index):
                key.descr.append(text[:-1])
                text = ''
                index = self.handle_key(ind, des, index, descr, lines, key_list,
                                        self.get_outer_key(outer_key, key))
            else:
                text += des
        if text not in ['', '\n']:
            key.descr.append(text[:-1])
        self.add_key(key, key_list, outer_key)
        if self.is_correct_key(des, descr, index):
            _indent = indent
            if ind < indent:
                _indent = ind
                outer_key = outer_key[:-1]
            return self.handle_key(_indent, des, index, descr,
                                   lines, key_list, outer_key)
        return index

    def remove_spaces(self, line):
        tmp_line = line.lstrip(' ')
        return (len(line) - len(tmp_line), tmp_line)

    def is_correct_key(self, line, descr, index):
        return ((index > 1 and line != '\n') \
                or index == 0) and self.is_key_line(line)

    def is_key_line(self, line):
        def is_correct_indent(line, indent):
            return indent != -1 and indent < FIRST_BIG_SPACE and \
                   line[indent - 1] not in ['.', '!', '?']
        global KEY_LINE_LENGTH
        global FIRST_BIG_SPACE, INDENT

        words = list(filter(None, line.split(' ')))
        first_char = line[0]
        if first_char == '-':
            return True
        if (first_char in ['!', '?', '\\', '['] or \
           first_char.upper() != first_char):
            indent = line.find(INDENT)
            if len(words) < KEY_LINE_LENGTH:
                for ch in [')', '(', '.']:
                    if ch in line:
                        return False
                return True
            elif is_correct_indent(line, indent):
                return True
        return False

    def get_layouts(self):
        try:
            with open(self.filename, 'r') as _file:
                layouts = []
                lines = _file.readlines()[1:]
                inner_text = []
                for line in lines:
                    if line[0] not in [' ', '\n'] and line == line.upper():
                        if len(layouts) > 0:
                            layouts[-1].descr = inner_text
                        inner_text = []
                        layouts.append(self.Layout(title=line[:-1], descr=''))
                    else:
                        inner_text.append(line[:-1] if line != '\n' else line)
                layouts[-1].descr = inner_text
        except FileNotFoundError:
            print('[-] File wasn\'t found')
        return layouts
