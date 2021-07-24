from webscraping import WebScraper
from bs4 import BeautifulSoup
from time import sleep


class NCTM(WebScraper):

    def get_article_urls(self, journal_url):
        self.driver.get(journal_url)
        sleep(3)
        for i in range(2, 5):
            self.driver.find_element_by_xpath(f"//*[@id='container-11531-item-11521']/div/div/div/ul/li[{i}]/div/a").click()
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        self.driver.quit()
        issue_urls = []
        for volume in soup.find_all(class_="ajax-node-opener type-volume text-title c-Link-emphasize color-text my-2 py-3 border-bottom-dark open"):
            if self.in_date_range(volume.text):
                for issue in volume.find_all(class_="c-Button--link", href=True):
                    issue_urls.append(f"https://pubs.nctm.org{issue.get('href')}")

        article_urls = []
        for issue_url in issue_urls:
            issue = self.get_html(issue_url)
            for article in issue.find_all(class_="type-article leaf has-access-icon text-title my-2 pt-0 pb-3"):
                article_url = article.find(class_="c-Button--link", href=True)
                article_urls.append(f"https://pubs.nctm.org{article_url.get('href')}")

        print(f"Number of issues found: {len(issue_urls)}")
        print(f"Number of article found: {len(article_urls)}")
        return article_urls

    def get_article_data(self, article_url):
        # article = self.get_html(article_url)

        self.driver.get(article_url)
        article = BeautifulSoup(self.driver.page_source, 'lxml')
        if article.title is not None:
            sleep(90)
            return self.get_article_data(article_url)

        # Download paper
        sleep(5)
        self.driver.find_element_by_xpath("//*[@id='pdf-download']").click()
        sleep(1)

        year = article.find("meta", attrs={'name': "citation_publication_date"})
        if year is None:
            year = article.find("meta", attrs={"name": "citation_online_data"})
        article_data = {
            'year': year.get('content')[:4] if year is not None else None,
            'journal': article.find("meta", attrs={'name': "citation_journal_title"}).get('content'),
            'title': article.find("meta", attrs={"name": "citation_title"}).get('content'),
            'volume': article.find("meta", attrs={"name": "citation_volume"}).get('content'),
            'issue': article.find("meta", attrs={"name": "citation_issue"}).get('content'),
            'first_page': article.find("meta", attrs={"name": "citation_firstpage"}).get('content'),
            'last_page': article.find("meta", attrs={"name": "citation_lastpage"}).get('content'),
            'doi': article.find("meta", attrs={"name": "citation_doi"}).get('content'),
            'authors': [author.get('content') for author in article.find_all("meta", attrs={"name": "citation_author"})]
        }
        return article_data
