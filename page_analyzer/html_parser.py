from bs4 import BeautifulSoup


class HTMLParser:

    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

    def get_title(self):
        title_tag = self.soup.title
        return title_tag.string if title_tag else None

    def get_h1(self):
        h1_tag = self.soup.h1
        return h1_tag.string if h1_tag else None

    def get_content(self):
        content = [meta.get('content')
                   for meta in self.soup.find_all('meta')
                   if meta.get('name') == 'description'
                   ]

        return content[0][:255] if content else None

    def get_data_page(self):
        result = {
            'title': self.get_title(),
            'h1': self.get_h1(),
            'content': self.get_content()
        }
        return result
