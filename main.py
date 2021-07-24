import csv
from webscraping import WebScraper
from nctm import NCTM
from science_direct import ScienceDirect
from springer import Springer
from taylor_francis import TaylorFrancis
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver

publishers = {
    'jresematheduc': None, 'jresemtheduc': None, 'j': None, 'S0732': None, 's10649': Springer,
    '14794802': TaylorFrancis, 's10763': Springer, 's13394': Springer, '10986065': TaylorFrancis, 's10857': Springer,
    's11858': Springer,
}

generic_scraper = WebScraper()

firefox_profile = FirefoxProfile()
firefox_profile.set_preference("browser.download.folderList", 2)
firefox_profile.set_preference("browser.download.dir",
                               "/Users/jacobstrauss/Documents/Python/Applications/research_scanner_v2/articles/")
firefox_profile.set_preference("browser.download.useDownloadDir", True)
firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                               "application/pdf;text/plain;application/text;text/xml;application/xml")
firefox_profile.set_preference("pdfjs.disabled", True)

driver = webdriver.Firefox(firefox_profile=firefox_profile)

with open("papers.csv", "w") as csv_file:
    writer = csv.writer(csv_file)
    with open("new_doi.txt", "r") as doi_file:
        for i, doi in enumerate(doi_file, start=1856):
            extension = doi.split('/')[4].split('-')[0].strip().split('.')[0]
            publisher = publishers[extension]
            if publisher is not None:
                scraper = publisher()
                setattr(scraper, 'driver', driver)
                print()
                print(scraper.__class__.__name__)
            else:
                continue
            article_data = scraper.get_article_data(doi)

            # Format filename and write data to csv
            apa_citation = scraper.apa_citation(article_data)
            writer.writerow([i, article_data['journal'], article_data['volume'], article_data['issue'], apa_citation])

            # Download paper
            if 'download_link' in article_data:
                download_link = article_data['download_link']
                try:
                    author = article_data['authors'][0]
                except:
                    author = 'ERROR'
                filename = f"{i} - {article_data['year']} - {author} - {article_data['journal']}"
                scraper.download_article(download_link, filename)

            print(f"({i-1855}) Downloaded paper: {doi}")

# import re
# import csv

# date_regex = re.compile(r"\((\d\d\d\d)\)")

# with open('papers.csv', 'r') as csv_file:
#     reader = csv.reader(csv_file)
#     for entry in reader:
#         date = date_regex.search(entry[-1])
#         print(date.group(1))
