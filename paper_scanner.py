
# ------ PAPER SCANNER ------

# This program will download papers from a list of URLs saved in an excel spreadsheet. The program was intended to be used
# in conjunction with the accompanying "literature_finder.py" file.

# The program will download and retrieve the meta-data for papers stored on JStor, Springer and Elsevier. It saves the
# paper as a pdf, giving it the filename: ID_NUMBER - YEAR - AUTHOR NAME - JOURNAL - VOLUME(ISSUE). The program will also
# saves the paper's meta-data to a spreadsheet using APA formatting.

# Rather than terminating, when the program encounters an error with downloading one of the papers it prints the cause of
# the error and moves on to the next URL. It will however save the paper's meta-data to the spreadsheet.

# The program uses the Firefox browser to access the papers. This will need to be installed prior to its excecution.
# See https://www.mozilla.org/ for more details.

# DISCLAIMER: This program was used to access articles at a specific point in time. There is no guarantee that the program will work in the future as the websites
# may have altered their layout.

# --- Imports ---

# requests, bs4, openpyxl and selenium must be installed before running the program. These can be installed by simply entering pip install {module_name} in the command
# line. See https://pip.pypa.io/en/stable/ for more details.

from bs4 import BeautifulSoup
import requests
import openpyxl
from selenium import webdriver
from time import sleep
import re

# User agent header to tell the webpage that a legitimate browser is accessing the page. This has been classified, and should be changed by the user.
headers = {
    'User-Agent': '****** CHANGE_ME *******'}


def springer(number, url):
    global headers
    res = requests.get(url, headers=headers)
    try:
        res.raise_for_status()
    except Exception as exc:
        print(exc)
        print(f'\nInvalid URL: {url}')
        update_spreadsheet(ref=number, journal=None, date=None, apa=None, error=True, url=url, description=exc)
        return
    soup = BeautifulSoup(res.text, 'lxml')

    authors = []
    for data in soup.find_all("meta"):
        if data.get("name", None) == "prism.publicationName":
            journal = data.get("content", None)
        elif data.get("name", None) == 'dc.title':
            title = data.get("content", None)
        elif data.get("name", None) == 'prism.publicationDate':
            date = data.get("content", None)
        elif data.get("name", None) == 'prism.volume':
            volume = data.get("content", None)
        elif data.get("name", None) == 'prism.number':
            issue = data.get("content", None)
        elif data.get("name", None) == 'dc.creator':
            authors.append(data.get("content", None))
        elif data.get("name", None) == 'prism.startingPage':
            start_page = data.get("content", None)
        elif data.get("name", None) == 'prism.endingPage':
            end_page = data.get("content", None)
        elif data.get("name", None) == 'citation_doi':
            doi = data.get("content", None)

    try:
        working_date = date.split('-')[0]
    except:
        working_date = 'ERROR'
    try:
        first_author = authors[0].split()[-1]
    except:
        first_author = 'ERROR'
    try:
        file_name = f"{number} - {working_date} - {first_author} - {journal} - {volume}"
    except:
        file_name = f"{number}"

    download_link = soup.find(class_="c-pdf-download__link")
    r = requests.get(download_link.get("href", None), stream=True)
    try:
        r.raise_for_status()
    except Exception as exc:
        print(exc)
        print(f'\nDownload Error: {url}')
        update_spreadsheet(ref=number, journal=None, date=None, apa=None, error=True, url=url, description=exc)
        return

    with open(f"/Users/jacobstrauss/Documents/Python/Applications/Research Scanner/Unread Papers/{file_name}.pdf",
              'wb') as f:
        f.write(r.content)

    reference = apa_citation(authors=authors, date=working_date, title=title, journal=journal, volume=volume,
                             issue=issue, start_page=start_page, end_page=end_page, doi=doi)
    update_spreadsheet(number, journal, working_date, reference)
    print(reference)
    return journal, working_date


def elsevier(number, url):
    global headers
    global browser

    browser.get(url)
    sleep(2)
    try:
        browser.find_element_by_xpath("// *[ @ id = 'pdfLink']").click()
    except:
        exc = "Unable to find element with specified Xpath"
        print(exc)
        update_spreadsheet(ref=number, journal=None, date=None, apa=None, error=True, url=url, description=exc)
        return
    soup = BeautifulSoup(browser.page_source, 'lxml')

    for data in soup.find_all("meta"):
        if data.get("name", None) == "citation_journal_title":
            journal = data.get("content", None)
        elif data.get("name", None) == 'citation_title':
            title = data.get("content", None)
        elif data.get("name", None) == 'citation_publication_date':
            date = data.get("content", None)
        elif data.get("name", None) == 'citation_volume':
            volume = data.get("content", None)
        elif data.get("name", None) == 'citation_firstpage':
            start_page = data.get("content", None)
        elif data.get("name", None) == 'citation_lastpage':
            end_page = data.get("content", None)
        elif data.get("name", None) == 'citation_doi':
            doi = data.get("content", None)

    authors = []
    for author in soup.find_all(class_="author size-m workspace-trigger"):
        authors.append(f"{author.find(class_='text given-name').text} {author.find(class_='text surname').text}")

    try:
        working_date = date.split('/')[0]
    except:
        working_date = 'ERROR'
    try:
        first_author = authors[0].split()[-1]
    except:
        first_author = 'ERROR'
    try:
        file_name = f"{number} - {working_date} - {first_author} - {journal} - {volume}"
    except:
        file_name = f"{number}"

    download_button = soup.find(class_="popover-content-inner")
    download_url = download_button.find(class_="link-button u-margin-s-bottom link-button-primary").get("href", None)
    browser.get(f'https://www.sciencedirect.com{download_url}')
    sleep(1)
    r = requests.get(browser.current_url, stream=True, headers=headers)
    try:
        r.raise_for_status()
    except Exception as exc:
        print(exc)
        print(f'\nDownload Error: {url}')
        update_spreadsheet(ref=number, journal=None, date=None, apa=None, error=True, url=url, description=exc)
        return

    with open(f"/Users/jacobstrauss/Documents/Python/Applications/Research Scanner/Unread Papers/{file_name}.pdf",
              'wb') as f:
        f.write(r.content)

    try:
        end_page
    except UnboundLocalError:
        end_page = ''

    reference = apa_citation(authors=authors, date=working_date, title=title, journal=journal, volume=volume,
                             start_page=start_page, doi=doi, end_page=end_page)
    print(reference)
    update_spreadsheet(number, journal, working_date, reference)

    return journal, working_date


def taylor_francis(number, url):
    global headers
    res = requests.get(url, headers=headers)
    try:
        res.raise_for_status()
    except Exception as exc:
        print(exc)
        print(f'\nInvalid URL: {url}')
        update_spreadsheet(ref=number, journal=None, date=None, apa=None, error=True, url=url, description=exc)
        return
    soup = BeautifulSoup(res.text, 'lxml')

    authors = []
    for data in soup.find_all("meta"):
        if data.get("name", None) == "citation_journal_title":
            journal = data.get("content", None)
        elif data.get("name", None) == 'dc.Title':
            title = data.get("content", None)
        elif data.get("name", None) == 'dc.Creator':
            authors.append(data.get("content", None))
        elif data.get("name", None) == 'dc.Date':
            date = data.get("content", None)
        elif data.get("name", None) == 'dc.Source':
            doi = data.get("content", None)

    issue_volume = soup.find(class_='issue-heading').text
    volume_regex = re.compile(r'(Volume )(\d+)')
    issue_regex = re.compile(r'(Issue )(\d+)')

    try:
        volume = volume_regex.search(issue_volume).group(2)
    except AttributeError:
        print(f"Volume Error: \n{url}\n{journal}")
        volume = ''
    try:
        issue = issue_regex.search(issue_volume).group(2)
    except AttributeError:
        print(f"Issue Error: \n{url}\n{journal}")
        volume = ''

    page_numbers = soup.find(id="45057865-d60c-414c-bc81-646debb621b0").text
    page_regex = re.compile(r'(\d+)-(\d+)')
    try:
        start_page = page_regex.search(page_numbers).group(1)
    except:
        start_page = 'ERROR'
    try:
        end_page = page_regex.search(page_numbers).group(2)
    except:
        end_page = 'ERROR'

    try:
        working_date = date[-4:]
    except:
        working_date = 'ERROR'
    try:
        first_author = authors[0].split()[-1]
    except:
        first_author = 'ERROR'
    try:
        working_doi = doi[-29:]
    except:
        working_doi = 'ERROR'
    try:
        file_name = f"{number} - {working_date} - {first_author} - {journal} - {volume}"
    except:
        file_name = f"{number}"

    r = requests.get(f'https://www.tandfonline.com/doi/pdf/{working_doi}?needAccess=true', stream=True, headers=headers)
    try:
        r.raise_for_status()
    except Exception as exc:
        print(exc)
        print(f'\nDownload Error: {url}')
        update_spreadsheet(ref=number, journal=None, date=None, apa=None, error=True, url=url, description=exc)
        return

    with open(f"/Users/jacobstrauss/Documents/Python/Applications/Research Scanner/Unread Papers/{file_name}.pdf",
              'wb') as f:
        f.write(r.content)

    reference = apa_citation(authors=authors, date=working_date, title=title, journal=journal, volume=volume,
                             start_page=start_page, end_page=end_page, doi=working_doi, issue=issue)
    print(reference)
    update_spreadsheet(number, journal, working_date, reference)

    return journal, working_date


def reformat_authors(authors):
    if isinstance(authors, list):
        apa = []
        for fullname in authors:
            author_reformat = []
            try:
                names = fullname.split()
            except AttributeError:
                apa.append('ERROR')
                continue
            author_reformat.append(names[-1])
            for name in names[:-1]:
                author_reformat.append(f'{name[0]}.')
            if fullname == authors[-1] and len(authors) > 1:
                author_reformat.insert(0, '&')
            apa.append(' '.join(author_reformat))
        return ', '.join(apa)
    else:
        return 'ERROR'


def apa_citation(authors, date, title, journal, volume, start_page, end_page, doi, issue=''):
    author = reformat_authors(authors)
    if issue == '':
        if end_page == '':
            return f"{author} ({date}). {title}. {journal}, {volume}, {start_page}. https://doi.org/{doi}"
        else:
            return f"{author} ({date}). {title}. {journal}, {volume}, {start_page}-{end_page}. https://doi.org/{doi}"
    else:
        if end_page == '':
            return f"{author} ({date}). {title}. {journal}, ({volume}){issue}, {start_page}. https://doi.org/{doi}"
        else:
            return f"{author} ({date}). {title}. {journal}, ({volume}){issue}, {start_page}-{end_page}. https://doi.org/{doi}"


def update_spreadsheet(ref, journal, date, apa, error=False, url=None, description=None):
    global sheet
    if error:
        sheet[f'A{ref + 2}'] = ref
        sheet[f'B{ref + 2}'] = description
        sheet[f'C{ref + 2}'] = url

    else:
        sheet[f'A{ref + 2}'] = ref
        sheet[f'B{ref + 2}'] = journal
        sheet[f'C{ref + 2}'] = date
        sheet[f'D{ref + 2}'] = apa


def addresses():
    for row in range(1778):
        yield data_sheet[f'D{row + 1}'].value


if __name__ == '__main__':

    # --- Loading sheets ---
    wb = openpyxl.load_workbook('Literature Spreadsheet.xlsx')
    sheet = wb['Sheet1']
    db = openpyxl.load_workbook('All Articles.xlsx')
    data_sheet = db['Sheet']

    # --- Adjusting browser settings ---
    browser = webdriver.Firefox()
    browser.get('https://www.sciencedirect.com/enhanced-reader/settings')
    sleep(3)
    browser.find_element_by_css_selector('.switch-check').click()
    sleep(3)

    journal_count = {}
    for num, paper_url in enumerate(addresses()):
        if 'springer' in paper_url:
            j = springer(num, paper_url)
            if j[0] in journal_count:
                journal_count[j] += 1
            else:
                journal_count.update({j: 1})
        elif 'sciencedirect' in paper_url:
            j = elsevier(num, paper_url)
            if j[0] in journal_count:
                journal_count[j] += 1
            else:
                journal_count.update({j: 1})
        elif 'tandfonline' in paper_url:
            j = taylor_francis(num, paper_url)
            if j[0] in journal_count:
                journal_count[j] += 1
            else:
                journal_count.update({j: 1})

        wb.save('test_one.xlsx')
    print(journal_count) # Print number and type of articles
