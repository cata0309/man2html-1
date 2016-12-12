from text_attrs import Key, Layout, Paragraph


class HTMLMaker:
    def __init__(self, filename, layouts):
        self.filename = filename
        self.layouts = layouts

    def write2file(self, html_page):
        with open(self.filename.rsplit('.', maxsplit=1)[-2] + '.html', 'w') as _file:
            _file.write(html_page)

    def attr2html(self, key, indent=1):
        html = ''
        if type(key) == Key:
            html += '<p style="margin-left:{}px">{}</p>\n' \
                    .format(str(indent * 40), key.name)
        else:
            html += '<p style="margin-left:{}px font-size:18px"</p>\n' \
                    .format(str(indent * 40), key.title)
        for ds in key.descr:
            if type(ds) in [Key, Paragraph]:
                html += self.attr2html(ds, indent + 1)
            else:
                html += '<p style="margin-left: {}px">{}</p>\n' \
                        .format(str((indent + 1) * 40), ds)
        return html

    def paragraph2html(self, paragraph, indent=1):
        html = ''
        html += ''

    def man2html(self):
        self.write2file(self.make_htmlfile())

    def make_htmlfile(self):
        html_page = ''
        for layout in self.layouts:
            html_page += '<h3>{}</h3>\n'.format(layout.title)
            for ds in layout.descr:
                if type(ds) in [Key, Paragraph]:
                    html_page += self.attr2html(ds)
                else:
                    for part in ds.split('\n'):
                        html_page += '<p style="margin-left: 40px">{}</p>\n' \
                                     .format(part)
        return html_page
