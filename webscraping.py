from bs4 import BeautifulSoup
import requests



class WebScraper:

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
    }

    def __init__(self, date_range=('2018', '2019', '2020')):
        self.date_range = date_range

    def get_article_urls(self, journal_url):
        pass

    def get_html(self, url):
        req = requests.get(url, headers=self.headers)
        try:
            req.raise_for_status()
        except Exception as exc:
            raise exc
        soup = BeautifulSoup(req.text, 'lxml')
        return soup

    def in_date_range(self, text):
        for date in self.date_range:
            if date in text:
                return True
        return False

    def get_articles(self, journal_url):
        articles = self.get_article_urls(journal_url)
        filename = journal_url.split('/')
        self.save_data(articles, filename)

    @staticmethod
    def save_data(data, filename):
        with open(f"{filename}.txt", "w") as file:
            for entry in data:
                file.write(entry + '\n')

    @staticmethod
    def download_article(article_url, filename):
        res = requests.get(article_url, stream=True)
        try:
            res.raise_for_status()
        except Exception as exc:
            print(exc)
            print(f'Download Error: {article_url}')
            return
        with open(f"./articles/{filename}.pdf", 'wb') as file:
            file.write(res.content)

    @staticmethod
    def reformat_authors(authors):
        if not authors:
            return 'ERROR'
        apa_formatted_authors = []
        for fullname in authors:
            author_reformat = []
            try:
                names = fullname.split()
            except AttributeError:
                apa_formatted_authors.append('ERROR')
                print("Author error")
                continue
            author_reformat.append(names[-1])
            for name in names[:-1]:
                author_reformat.append(f'{name[0]}.')
            if fullname == authors[-1] and len(authors) > 1:
                author_reformat.insert(0, '&')
            apa_formatted_authors.append(' '.join(author_reformat))
        return ', '.join(apa_formatted_authors)

    def apa_citation(self, data: dict):
        authors = self.reformat_authors(data['authors'])
        doi = f"https://doi.org/{data['doi']}" if not data['doi'].startswith('https') else data['doi']
        if not data['issue']:
            if not data['last_page']:
                return f"{authors} ({data['year']}). {data['title']}. {data['journal']}, {data['volume']}, " \
                       f"{data['first_page']}. {doi}"
            else:
                return f"{authors} ({data['year']}). {data['title']}. {data['journal']}, {data['volume']}, " \
                       f"{data['first_page']}-{data['last_page']}. {doi}"
        else:
            if not data['last_page']:
                return f"{authors} ({data['year']}). {data['title']}. {data['journal']}, " \
                       f"{data['volume']}{data['issue']}, {data['first_page']}. {doi}"
            else:
                return f"{authors} ({data['year']}). {data['title']}. {data['journal']}, " \
                       f"{data['volume']}{data['issue']}, {data['first_page']}-{data['last_page']}. {doi}"
