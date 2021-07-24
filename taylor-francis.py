import re
from webscraping import WebScraper


class TaylorFrancis(WebScraper):

    def get_article_urls(self, journal_url):

        # Get links to each volume
        journal = self.get_html(journal_url)
        volume_urls = []
        for list_item in journal.find_all(class_="vol_li"):
            if self.in_date_range(list_item.text):
                volume_url = list_item.find(class_="hidden", href=True)
                if volume_url is not None:
                    volume_urls.append(f"https://www.tandfonline.com{volume_url.get('href')}")
                else:
                    print(f"Could not find volume link for {list_item.text}")

        if len(volume_urls) == 0:
            raise Exception("Invalid journal page. Webpage must contain a list of all issues. See "
                            "https://www.tandfonline.com/loi/rrme20 for an example")

        # Get issue links for each volume
        issue_urls = []
        for volume_url in volume_urls:
            journal = self.get_html(volume_url)
            volume = journal.find(class_="vol_li active loaded")
            if volume is not None:
                for issue_url in volume.find_all(class_="issue-link", href=True):
                    issue_urls.append(f"https://www.tandfonline.com{issue_url.get('href')}")
            else:
                print(f'Could not find an issue link for {volume_url}')

        # Get paper urls from each issue
        article_urls = []
        for issue_url in issue_urls:
            issue = self.get_html(issue_url)
            for paper in issue.find_all(class_="articleEntry"):
                title = paper.find(class_="art_title linkable")
                if title is not None:
                    article_url = title.find(class_="ref nowrap", href=True)
                    if article_url is not None:
                        article_urls.append(f"https://www.tandfonline.com{article_url.get('href')}")
                    else:
                        print(f'Could not find an article link for {issue_url}')
                else:
                    print(f'Could not find title link for {paper}')
        print(f"Number of issues found: {len(issue_urls)}")
        print(f"Number of article found: {len(article_urls)}")
        return article_urls

    def get_article_data(self, article_url):
        article = self.get_html(article_url)
        article_data = {
            'year': article.find("meta", attrs={'name': "dc.Date"}).get('content')[-4:],
            'journal': article.find("meta", attrs={'name': "citation_journal_title"}).get('content'),
            'title': article.find("meta", attrs={"name": "dc.Title"}).get('content'),
            'doi': article.find("meta", attrs={"name": "dc.Source"}).get('content'),
            'authors': [author.get('content') for author in article.find_all("meta", attrs={"name": "dc.Creator"})],
            'download_link': f"https://www.tandfonline.com{article.find(class_='show-pdf', href=True).get('href')}"
        }

        # Find page numbers
        header = article.find(class_="widget responsive-layout none publicationContentHeader widget-none widget-compact-all").text
        regex_pages = re.search(r"Pages (\d*)-(\d*)", header)
        article_data.update({'first_page': regex_pages.group(1) if regex_pages is not None else ''})
        article_data.update({'last_page': regex_pages.group(2) if regex_pages is not None else None})

        # Find volume and issue
        article_index = article.find(class_="issue-heading").text
        regex_volume = re.search(r"Volume (\d*)", article_index)
        regex_issue = re.search(r"Issue (\d*)", article_index)
        article_data.update({'volume': regex_volume.group(1) if regex_volume is not None else ''})
        article_data.update({'issue': regex_issue.group(1) if regex_issue is not None else None})
        return article_data
