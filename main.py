# AUTHOR: @hendrik_bgr
# For educational use only
# Free for ever

from requests_html import HTMLSession
import requests
import re
import threading
import queue
import itertools
import time
from colorama import Fore, Back, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin


version = "1.0"

try:
    with open('urls.txt', 'r') as file:
        urls = [line.rstrip() for line in file.readlines()]
except FileNotFoundError:
    raise Exception('urls.txt not found.')

url_count = len(urls)

print('--------------------------------------')
print('- Easy Proxy Scraper & Checker {} -'.format(version))
print('- Found {} URLS to Scrape            -'.format(url_count))
print('--------------------------------------')
print()
print()

# Scrape Proxies
proxy_set = set()
session = HTMLSession()


def scrape_proxies(url):
    try:
        r = session.get(url)
        proxies_found = re.findall(r'\d+\.\d+\.\d+\.\d+\:\d+', r.text)
        print(f"Found {len(proxies_found)} proxies on {url}")
        proxy_set.update(proxies_found)
    except Exception as e:
        print(f"Error scraping {url}: {e}")

for url in urls:
    print('Crawling Proxies from: ', url)
    scrape_proxies(url)  # Scrape the initial URL

    try:
        # Scrape all URLs found on the page
        all_links = session.get(url).html.absolute_links
        for link in all_links:
            scrape_proxies(link)
    except Exception as e:
        print(f"Error scraping links from {url}: {e}")

session.close()

# Save Proxies to File
with open('proxies.txt', mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(proxy_set))

print('TOTAL NUMBER OF PROXIES CRAWLED: ', len(proxy_set))

# Check Proxies
def check_proxy(proxy):
    """
    Check if a proxy is working by attempting to access a known website through it.
    Returns True if the proxy is good, False otherwise.
    """
    test_url = 'http://www.google.com'
    proxies = {
        'http': proxy,
        'https': proxy
    }

    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working.")
            return True
    except requests.RequestException as e:
        print(f"Proxy {proxy} failed: {e}")

    return False

def main():
    with open('proxies.txt', 'r') as file:
        proxies = file.read().splitlines()

    total_proxies = len(proxies)
    print(f"Total proxies to check: {total_proxies}")

    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                is_good = future.result()
                if is_good:
                    with open('checked.txt', 'a') as out_file:
                        out_file.write(proxy + '\n')
            except Exception as e:
                print(f"Error checking proxy {proxy}: {e}")

if __name__ == "__main__":
    main()
