import argparse
import csv
import re
import requests
import time
from functools import wraps
from configparser import ConfigParser
from bs4 import BeautifulSoup as bs

def timer(function):
    @wraps(function)
    def measure(*args, **kwargs):
        start = time.time()
        try:
            entries, entry_title = function(*args, **kwargs)
            return entries, entry_title
        finally:
            end = time.time()
            print(f"Total execution time {entry_title}: {end-start:.2f} ms")
    return measure

def get_config(path):
    """[Read the config file]

    Args:
        path ([str]): [Path of the config file]

    Returns:
        [dic]: [links dictionaty and user-agent for requests]
    """
    with open(path, 'r') as f:
        config = ConfigParser()
        config.read_file(f)
        
        links_dic = {baslik: link for baslik, link in config.items('links')}
        headers = {'user-agent': config.get('headers', 'user-agent')}
    
    return links_dic, headers
        
@timer
def getEntries(url, headers, sleep_time):
    """[Return entries and baslik]

    Args:
        url ([str]): [url of the first page of the baslik without the &p=[page_number] part]
        headers ([str]): [user-agent to be able to enter eksi]
        sleep_time (float, optional): [Sleep time between every page]

    Returns:
        [list]: [entries and entry_title]
    """
    r = requests.get(url, headers = headers)
    soup = bs(r.content, features='html.parser')
    
    try:
        count_line = str(soup.select_one('div.pager'))
        page_count = int(re.findall(r'\d+', count_line)[-1])
    except:
        page_count = 1

    entries = []
    for i in range(1, page_count + 1):
        r = requests.get(url + '?p=' + str(i), headers=headers)
        
        time.sleep(sleep_time)
        
        soup = bs(r.content, features='html.parser')
        
        entry_section = soup.select('li div.content')
        
        for section in entry_section:
            entry = str(section.get_text()).strip()
            entries.append(entry)
            
    entry_title = soup.select_one('h1#title a').get_text()
    
    return entries, entry_title

def to_csv(entries, entry_title):
    """[Save to the same directory]

    Args:
        entries ([list]): [List of the entries]
        entry_title ([str]): [Name of the saved file and header of the csv]
    """
    with open(entry_title + '.csv', 'w', newline='') as myfile:
        writer = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        writer.writerow([entry_title])
        writer.writerows(zip(entries))

def main():
    parser = argparse.ArgumentParser(description='Ekşi Web Scraper')
    parser.add_argument('-p','--path', type=str, help='Path of the config file')
    parser.add_argument('-t','--time', default=1, type=float, help='Sleep time between the pages of same entry')
    args =parser.parse_args()
    
    if not args.path:
        parser.print_help()
        exit()
    else:
        links_dic, headers = get_config(args.path)
    
    for url in links_dic.values():
        entries, entry_title = getEntries(url, headers, args.time)
        to_csv(entries, entry_title)
    
if __name__ == '__main__':
    main()