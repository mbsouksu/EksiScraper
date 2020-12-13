from bs4 import BeautifulSoup as bs
import requests
import csv
import time
from functools import wraps

def timer(function):
    @wraps(function)
    def measure(*args, **kwargs):
        start = time.time()
        try:
            return function(*args, **kwargs)
        finally:
            end = time.time()
            print(f"Total execution time: {end-start:.2f} ms")
    return measure


def totPage(url, headers):
    """[For calculation of the number of entry pages for given başlık]

    Args:
        url : [url of the first page of the başlık without the &p=[page_number] part]
        headers : [user-agent to be able to enter ekşi]
    """
    #Load the page
    r = requests.get(url, headers = headers)
    
    #Convert to BeautifulSoup Object
    soup = bs(r.content, features='html.parser')
    
    #get the total number of pages
    #Page is rendered by Javascipt, so we extract the page count a bit brute force. 

    try:
        page_count = int(str(soup.select_one('div.pager'))[-10:-8])
    except:
        page_count = 1
        
    return page_count

@timer
def getEntries(url, headers, tot_page=1, sleep_time=2):
    
    print(f'Expected time is {sleep_time*tot_page}')
    entries = []
    for i in range(1, tot_page + 1):
        r = requests.get(url + '?p=' + str(i), headers=headers)
        
        time.sleep(sleep_time)
        
        soup = bs(r.content, features='html.parser')
        
        entry_section = soup.select('li div.content')
        
        for section in entry_section:
            entry = str(section.get_text()).strip()
            entries.append(entry)
            
    entry_title = soup.select_one('h1#title a').get_text()
    
    return entries, entry_title


def to_csv(entries, filename, title='Entries'):
    
    with open(filename, 'w', newline='') as myfile:
        writer = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        writer.writerow([title])
        writer.writerows(zip(entries))

if __name__ == '__main__':
    url = input('Enter the url of the first page of the entry page: ')
    headers = {'user-agent': input('Enter the user-agent. Write my user agent in google: ')}
    tot_page = totPage(url= url,headers= headers)
    entries, entry_title = getEntries(url= url, headers= headers, tot_page= tot_page)
    filename = input('Enter the filename for saving: ') + '.csv'
    to_csv(entries=entries, filename=filename, title=entry_title)
