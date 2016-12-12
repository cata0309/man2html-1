from recordclass import recordclass
from text_attrs import Key, Layout, Paragraph

import re


main_titles = ['NAME', 'SYNOPSIS', 'DESCRIPTION', 'OPTIONS', '']
KEY_LINE_LENGTH = 5
PARAGRAPH_WORDS_LENGTH = 4
INDENT = '  '
FIRST_BIG_SPACE = 25


class ManParser:
    def __init__(self, filename):
        self.filename = filename

        self.KeyName = recordclass('KeyName', 'name arg')

        self.url = re.compile(r'http[s]?://(?:[a-zA-Z0-9$-_@.&+!*\(\),]|'
                               '(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def parse(self):
        layouts = self.get_layouts()
        for layout in layouts:
            title, descr = layout.get_params()
            if title in ['OPTIONS', 'DESCRIPTION', 'DEFINITIONS']:
                layout.descr = self.parse_layout_description(title, descr)
            layout.descr = self.parse_paragraphs(self.clear_lines(layout.descr))
            layout.descr = self.prettify_description(layout.descr)
        return layouts

    def clear_lines(self, lines):
        new_lines = []
        for line in lines:
            if type(line) == str:
                new_lines.append(self.remove_spaces(line))
            else:
                new_lines.append(line)
        return new_lines

    def is_paragraph(self, line):
        global PARAGRAPH_WORDS_LENGTH
        return len(line.split(' ')) < PARAGRAPH_WORDS_LENGTH and \
               line not in ['', '\n'] and line[0] == line[0].upper() \
               and line.find('.') == -1 and line[1] == line[1].lower()

    def parse_paragraphs(self, layout_descr):
        cur_par_indent = -1
        description, outer_paragraphs = [], []
        ds_iter = iter(layout_descr)
        for ds in ds_iter:
            if type(ds) != Key and self.is_paragraph(ds[1]):
                description += self.make_paragraph(ds[0], ds[1], ds_iter, par_list)
            else:
                description.append(ds)
        return description

    def make_paragraph(self, indent, title, ds_iter, par_list):
        cur_paragraph = Paragraph(title=title, descr=[])
        text = ''
        while True:
            try:
                ind, line = next(ds_iter)
            except StopIteration:
                if cur_paragraph.descr != []:
                    par_list.append(cur_paragraph)
                return
            if ind <= indent and line != '\n':
                break
            if self.is_paragraph(line):
                cur_paragraph.descr += text
                cur_paragraph.descr += self.make_paragraph(ind, line, ds_iter)
                text = ''
            else:
                text += line
        if text not in ['', '\n']:
            cur_paragraph.descr.append(text)
        par_list.append(cur_paragraph)
        if self.is_paragraph(line):
            self.make_paragraph(ind, line, ds_iter, par_list)

    def parse_layout_description(self, title, descr):
        parsed = []
        cur_paragraph_indent = -1
        lines = iter(descr)

        index = -1
        for line in lines:
            index += 1
            indent, line = self.remove_spaces(line)

            if self.is_correct_key(line, descr, index):
                keys = []
                index = self.handle_key(indent, line, index,
                                        descr, lines, keys)
                parsed += keys
            else:
                parsed += [(indent, line)]
        return parsed

    def prettify_description(self, descr):
        pret_descr = []
        prev_text = ''
        for line in list(filter(None, descr)):
            if type(line) in [Key, Paragraph]:
                pret_descr.append(prev_text)
                prev_text = ''
                title = line.name if type(line) == Key else line.title
                pret_descr.append(type(line)(title,
                                      self.prettify_description(line.descr)))
            else:
                prev_text += (line if type(line) != tuple else line[1]) + ' '
        pret_descr.append(prev_text)
        return pret_descr

    def get_name_description(self, words):
        global KEY_LINE_LENGTH

        words = list(filter(None, words))
        if len(words) < KEY_LINE_LENGTH:
            return (' '.join(words), [])
        else:
            for word, index in zip(words, range(len(words))):
                if word[0] == word[0].upper() and index > 0:
                    return (' '.join(words[:index]),
                            [' '.join(filter(None, words[index:]))])
            return (' '.join(words[:2]), [' '.join(filter(None, words[2:]))])

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

    def append_text(self, key, text):
        if text not in ['', '\n']:
            key.descr.append(text[:-1])

    def append_key2list(self, key, outer_key, key_list, text):
        self.append_text(key, text)
        self.add_key(key, key_list, outer_key)

    def handle_key(self, indent, line, index, descr, lines,
                   key_list, outer_key=None):
        text = ''
        name, description = self.get_name_description(line.split(' '))
        name = name.strip()
        key = Key(name, description)
        while True:
            try:
                ind, des = self.remove_spaces(next(lines))
            except StopIteration:
                self.append_key2list(key, outer_key, key_list, text)
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
        self.append_key2list(key, outer_key, key_list, text)
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
                        layouts.append(Layout(line[:-1], ''))
                    elif len(line.lstrip(' ').split(' ')) < 4:
                        inner_text.append(line)
                    else:
                        inner_text.append(line[:-1] if line != '\n' else line)
                layouts[-1].descr = inner_text
        except FileNotFoundError:
            print('[-] File wasn\'t found')
        return layouts
