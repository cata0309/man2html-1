class Layout:
    def __init__(self, title, descr):
        self.title = title
        self.descr = descr

    def get_params(self):
        return self.title, self.descr


class URL:
    def __init__(self, url):
        self.url = url


class Paragraph(Layout):
    def __init__(self, title, descr):
        super(self.__class__, self).__init__(title, descr)


class Key:
    def __init__(self, name, descr):
        self.name = name
        self.descr = descr
