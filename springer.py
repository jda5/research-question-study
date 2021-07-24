from webscraping import WebScraper


class Springer(WebScraper):

    def get_article_urls(self, journal_url):

        # Get links to each issue
        journal = self.get_html(journal_url)
        issue_urls = []
        for group_item in journal.find_all(class_="c-list-group__item"):
            issue_url = group_item.find(class_="u-interface-link u-text-sans-serif u-text-sm", href=True)
            if issue_url is not None:
                if self.in_date_range(issue_url.text):
                    issue_urls.append(f'https://link.springer.com{issue_url.get("href")}')
            else:
                print(f"No link was found for {group_item}")

        # Get paper urls from each issue
        article_urls = []
        for issue_url in issue_urls:
            issue = self.get_html(issue_url)
            for paper in issue.find_all(class_="c-list-group__item"):
                paper_url = paper.find(itemprop="url", href=True)
                article_urls.append(paper_url.get("href"))
        print(f"Number of issues found: {len(issue_urls)}")
        print(f"Number of article found: {len(article_urls)}")
        return article_urls

    def get_article_data(self, article_url):
        article = self.get_html(article_url)
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
            'authors': [author.get('content') for author in article.find_all("meta", attrs={"name": "citation_author"})],
            'download_link': article.find(class_="c-pdf-download__link").get('href')
        }
        return article_data
