from webscraping import WebScraper
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from time import sleep


class ScienceDirect(WebScraper):

    def get_article_urls(self, journal_url):
        self.driver.get(journal_url)
        sleep(5)
        try:
            issues = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_all_elements_located((By.XPATH, "//*[@id='all-issues']/ol/li"))
            )
        except TimeoutError as exc:
            raise exc
        for issue in issues:
            issue.click()
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        self.driver.quit()
        volume_urls = []
        for volume in soup.find_all(class_="accordion-panel js-accordion-panel"):
            if self.in_date_range(volume.text):
                for issue in volume.find_all(class_="issue-item u-margin-s-bottom"):
                    issue_url = issue.find(class_="anchor js-issue-item-link text-m", href=True)
                    volume_urls.append(f"https://www.sciencedirect.com{issue_url.get('href')}")
        article_urls = []
        for volume_url in volume_urls:
            volume = self.get_html(volume_url)
            for article in volume.find_all(class_="js-article-list-item article-item u-padding-xs-top u-margin-l-bottom"):
                article_url = article.find(class_="anchor article-content-title u-margin-xs-top u-margin-s-bottom",
                                           href=True)
                article_urls.append(f"https://www.sciencedirect.com{article_url.get('href')}")
        print(f"Number of volumes found: {len(volume_urls)}")
        print(f"Number of article found: {len(article_urls)}")
        return article_urls

    def get_article_data(self, article_url):
        self.driver.get(article_url)

        # Download paper
        sleep(5)
        self.driver.find_element_by_xpath("//*[@id='pdfLink']").click()
        sleep(1)
        article = BeautifulSoup(self.driver.page_source, 'lxml')
        popover = article.find(class_="popover-content-inner")
        button = popover.find(class_="link-button u-margin-s-bottom link-button-primary").get('href')
        self.driver.get(f"https://www.sciencedirect.com{button}")

        # article = self.get_html(article_url)

        year = article.find("meta", attrs={'name': "citation_publication_date"})
        if year is None:
            year = article.find("meta", attrs={"name": "citation_online_data"})

        article_data = {
            'year': year.get('content')[:4] if year is not None else None,
            'journal': article.find("meta", attrs={'name': "citation_journal_title"}).get('content'),
            'title': article.find("meta", attrs={"name": "citation_title"}).get('content'),
            'volume': article.find("meta", attrs={"name": "citation_volume"}).get('content'),
            'first_page': article.find("meta", attrs={"name": "citation_firstpage"}).get('content'),
            'doi': article.find("meta", attrs={"name": "citation_doi"}).get('content'),
        }
        # Get issue
        issue = article.find("meta", attrs={"name": "citation_issue"})
        article_data.update({'issue': issue.get('content') if issue is not None else None})

        # Get last page
        last_page = article.find("meta", attrs={"name": "citation_lastpage"})
        article_data.update({'last_page': last_page.get('content') if last_page is not None else None})

        # Get authors
        authors = []
        for author in article.find_all(class_="author size-m workspace-trigger"):
            authors.append(author.find(class_="text given-name").text.strip() + ' ' +
                           author.find(class_="text surname").text.strip())
        article_data.update({'authors': authors})

        return article_data
