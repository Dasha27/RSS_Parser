import urllib.request
import urllib.error
import xml.etree.ElementTree as elementTree
import json
import sys
import os
import re
from dateutil import parser
from itertools import islice
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter


class RSSParser:
    def __init__(self, url=None, limit=None, date=None, html_path=None, pdf_path=None):
        self.url = url
        if limit:
            if limit < 0:
                limit = 0
            elif limit > sys.maxsize:
                limit = None
        self.limit = limit
        if date:
            if len(date) != 8:
                try:
                    raise ValueError('RSS Parser stopped: incorrect date format')
                except ValueError as exc:
                    sys.exit(f'Please, enter the date in a correct format -> yyyymmdd - {exc} ')
        self.date = date
        self.tree_root = None
        self.news_dictionary = {}
        self.item_details = {}
        self.cached_news = []
        self.cache_directory = os.path.join('cache')
        self.html_path = html_path
        self.pdf_path = pdf_path
        self.remove_tags = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});|View Entire Post ')
        self.remove_elements = re.compile('{.*?}')

    def open_url(self):
        try:
            with urllib.request.urlopen(self.url) as page:
                response = page.read().decode('utf-8')
                self.tree_root = elementTree.fromstring(response)

        except ValueError as exc:
            sys.exit(f'Please, enter a correct url - {exc}')
        except TimeoutError as exc:
            sys.exit(f'The connection to the url timed out - {exc}')
        except urllib.error.URLError as exc:
            sys.exit(f'The connection to the url failed - {exc}')
        except elementTree.ParseError as exc:
            sys.exit(f'The url is not valid for RSS parsing - {exc}')

        self.url = re.sub('https?://(www)?', '', self.url)
        forbidden_symbols = ':/'
        for char in forbidden_symbols:
            self.url = self.url.replace(char, '_')

        if not os.path.exists(self.cache_directory):
            os.mkdir(self.cache_directory)

    def print_news_to_stdout(self):
        print('\n')
        for root_children in self.tree_root:
            for children in root_children:
                if children.text:
                    children.text = children.text.strip()
                    if children.text:
                        print(f'{children.tag.title()}: {children.text}')

        for item in islice(self.tree_root.iter('item'), self.limit):
            print('\n')
            for record in item.iter():
                if record.tag == 'pubDate':
                    record.text = str(parser.parse(record.text))
                if record.text:
                    record.text = re.sub(self.remove_tags, '', record.text)
                    record.tag = re.sub(self.remove_elements, '', record.tag)
                    print(f'{record.tag.title()}: {record.text}')
        print('\n')

    def save_news_to_dictionary(self):
        for root_children in self.tree_root:
            for children in root_children:
                if children.text:
                    children.text = children.text.strip()
                    if children.text:
                        self.news_dictionary[children.tag.title()] = children.text

        for number, item in enumerate(islice(self.tree_root.iter('item'), self.limit)):
            key = f'{item.tag.title()}_{str(number)}'
            self.news_dictionary[key] = dict()
            for record in item.iter():
                if record.tag == 'pubDate':
                    record.text = str(parser.parse(record.text))
                if record.text:
                    record.text = re.sub(self.remove_tags, '', record.text)
                    record.tag = re.sub(self.remove_elements, '', record.tag)
                    self.item_details[record.tag.title()] = record.text
            self.news_dictionary[key] = self.item_details
            self.cached_news.append(json.dumps(self.item_details))
            self.item_details = {}

    def convert_news_into_json(self):
        news_json = json.dumps(self.news_dictionary)
        print(f'\nThe RSS news in JSON format:\n{news_json}\n')

    def save_news_to_file(self):
        with open(os.path.join(self.cache_directory, "all_cache.txt"), 'a+') as file:
            file.seek(0)
            difference = set(self.cached_news) - set(file.read().splitlines())
            for new in list(difference):
                file.write("%s\n" % new)

        with open(f'{os.path.join(self.cache_directory, self.url)}.txt', 'a+') as file:
            file.seek(0)
            difference = set(self.cached_news) - set(file.read().splitlines())
            for new in list(difference):
                file.write("%s\n" % new)

    def get_news_from_cache(self):
        if self.url:
            file_name = self.url
        else:
            file_name = 'all_cache'
        try:
            with open(f'{os.path.join(self.cache_directory, file_name)}.txt', 'r') as file:
                news = 0
                for line in file:
                    stripped_date = eval(line).get('Pubdate').split(' ', 1)[0].replace('-', '')
                    if self.date in stripped_date:
                        news += 1
                        print('\n')
                        for i in eval(line):
                            print(f'{i}: {eval(line).get(i)}')
                        if news == self.limit:
                            break
                if not news:
                    try:
                        raise ValueError('RSS Parser stopped: no news was found for the entered date')
                    except ValueError as exc:
                        sys.exit(f'Please, enter the other date - {exc}')

        except FileNotFoundError as exc:
            sys.exit(f'The news from the specified source was not cached - {exc}')

    def get_news_from_cache_in_json(self):
        if self.url:
            file_name = self.url
        else:
            file_name = 'all_cache'
        try:
            with open(f'{os.path.join(self.cache_directory, file_name)}.txt', 'r') as file:
                news_json = {}
                for number, line in enumerate(file):
                    stripped_date = eval(line).get('Pubdate').split(' ', 1)[0].replace('-', '')
                    if self.date in stripped_date:
                        news_json[f'Item_{number}'] = eval(line)
                        if len(news_json) == self.limit:
                            break
                if not news_json:
                    try:
                        raise ValueError('RSS Parser stopped: no news was found for the entered date')
                    except ValueError as exc:
                        sys.exit(f'Please, enter the other date - {exc}')
                print(f'\nThe RSS news in JSON format:\n{json.dumps(news_json)}\n')

        except FileNotFoundError as exc:
            sys.exit(f'The news from the specified source was not cached - {exc}')

    def convert_news_to_html(self):
        try:
            if not os.path.exists(self.html_path):
                os.mkdir(self.html_path)
        except FileNotFoundError as exc:
            sys.exit(f'The path does not exist and cannot be created - {exc}')
        except OSError as exc:
            sys.exit(f'Please, enter a valid path - {exc}')

        try:
            file = open(os.path.join(self.html_path, f'{self.url}.html'), 'w')
        except PermissionError as exc:
            sys.exit(f'You cannot create a file here - {exc}')
        except FileNotFoundError as exc:
            sys.exit(f'The file path cannot be found - {exc}')

        for root_children in self.tree_root:
            for children in root_children:
                if children.text:
                    children.text = children.text.strip()
                    if children.text:
                        if children.tag == 'title':
                            file.write(f'<h1>{children.text}</h1>')
                        else:
                            file.write(f'<p>{children.tag.title()}: {children.text}</p>')

        for number, item in enumerate(islice(self.tree_root.iter('item'), self.limit)):
            file.write('<br>')
            for record in item.iter():
                if record.tag == 'pubDate':
                    record.text = str(parser.parse(record.text))
                if record.tag == 'title':
                    file.write(f'<h2>{record.text}</h2>')
                elif record.tag == 'link':
                    address = f'<a href="{record.text}">{record.text}</a>'
                    file.write(f'{record.tag.title()}: {address}<br>')
                else:
                    if record.text:
                        record.text = re.sub(self.remove_tags, '', record.text)
                        record.tag = re.sub(self.remove_elements, '', record.tag)
                        file.write(f'<p>{record.tag.title()}: {record.text}</p>')
                if ('content' in record.tag) or ('thumbnail' in record.tag):
                    file.write(f'<img src="{record.attrib["url"]}" width="400" height="300"><br>')
        file.close()

    def convert_news_to_pdf(self):
        try:
            if not os.path.exists(self.pdf_path):
                os.mkdir(self.pdf_path)
        except FileNotFoundError as exc:
            sys.exit(f'The path does not exist and cannot be created - {exc}')
        except OSError as exc:
            sys.exit(f'Please, enter a valid path - {exc}')

        style_body = ParagraphStyle(name='Times', fontName='Times', fontSize=15, leading=20)
        style_heading = ParagraphStyle(name='Times', fontName='Times-Bold', fontSize=15, leading=20)
        pdf_news = []
        doc = SimpleDocTemplate(
            os.path.join(self.pdf_path, f'{self.url}.pdf'),
            pagesize=letter,
            bottomMargin=40,
            topMargin=40,
            rightMargin=40,
            leftMargin=40)

        for root_children in self.tree_root:
            for children in root_children:
                if children.text:
                    children.text = children.text.strip()
                    if children.text:
                        if children.tag == 'title':
                            pdf_news.append(Paragraph(f'{children.text}', style_heading))
                        else:
                            pdf_news.append(Paragraph(f'{children.tag.title()}: {children.text}', style_body))
        pdf_news.append(Paragraph('<br/><br/><br/>', style_heading))

        for number, item in enumerate(islice(self.tree_root.iter('item'), self.limit)):
            pdf_news.append(Paragraph("<br/>"))
            for record in item.iter():
                if record.tag == 'pubDate':
                    record.text = str(parser.parse(record.text))
                if record.tag == 'title':
                    pdf_news.append(Paragraph(f'{record.text}', style_heading))
                elif record.tag == 'link':
                    address = f'<link href="{record.text}">{record.text}</link>'
                    pdf_news.append(Paragraph(f'{record.tag.title()}: {address}', style_body))
                else:
                    if record.text:
                        record.text = re.sub(self.remove_tags, '', record.text)
                        record.tag = re.sub(self.remove_elements, '', record.tag)
                        pdf_news.append(Paragraph(f'{record.tag.title()}: {record.text}', style_body))
                if ('content' in record.tag) or ('thumbnail' in record.tag):
                    image = Image(f'{record.attrib["url"]}')
                    image.drawHeight = 200
                    image.drawWidth = 300
                    pdf_news.append(image)
            pdf_news.append(Paragraph('<br/><br/>', style_body))

        try:
            doc.multiBuild(pdf_news)
        except PermissionError as exc:
            sys.exit(f'You cannot create a file here - {exc}')
        except FileNotFoundError as exc:
            sys.exit(f'The file path cannot be found - {exc}')
