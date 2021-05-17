from requests_html import HTMLSession
import requests
import re
import csv
import json
import sys
import urllib.request, socket
from threading import Thread
import asyncio
from sys import argv
import aiohttp


version = "0.0.2"
proxy_list = []
proxy_count = 0

try:
    with open('urls.txt', 'r') as file:
        urls = [ line.rstrip() for line in file.readlines()]
except FileNotFoundError:
    raise Exception('urls.txt not found.')

url_count = len(urls)

print('--------------------------------------')
print('- Easy Proxy Scraper & Checker {} -'.format(version))
print('- Found {} URLS to Scrape            -'.format(url_count))
print('--------------------------------------')
print()
print()
check_yn = input('Check proxies after? [y/n] ')

for url in urls:
    session = HTMLSession()
    print()
    print('Crawling Proxies from: ', url)

    # Get Proxy Content
    
    print()
    try:
        r = session.get(url)
        links = r.html.absolute_links
        links = str(links)
        links = links.replace('{', '')
        links = links.replace('}', '')
        links = links.split(',')
        for link in links:
            print('Link Scraped: ', link)

        # Get Proxies
        page = r.html.find('html', first=True)
        proxies_found = re.findall('\d+\.\d+\.\d+\.\d+\:\d+', page.html)
        proxy_list = proxy_list + proxies_found
        for proxy in proxy_list:
            print('Proxy found: ', proxy)
            proxy_count += 1
        
        for link in links:
            try:
                r = session.get(link)
                page = r.html.find('html', first=True)
                proxies_found = re.findall('\d+\.\d+\.\d+\.\d+\:\d+', page.html)
                proxy_list = proxy_list + proxies_found
                for proxy in proxy_list:
                    proxy_count += 1
                    print('Proxy found: ', proxy)
            except:
                pass
    except:
        pass
    
# Save Proxies to File
print('TOTAL NUMBER OF PROXIES CRAWLED: ', proxy_count)
with open('proxies.txt', mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(proxy_list))

if check_yn == 'y':
    
    for proxy in proxy_list:
        proxy_type = "http"
        test_url = "http://www.google.com"
        timeout_sec = 4

        # read the list of proxy IPs in proxyList from the first Argument given
        proxyList = proxy_list


        async def is_bad_proxy(ipport):
            try:
                session = aiohttp.ClientSession()
                resp = await session.get(test_url, proxy=ipport, timeout=timeout_sec)
                if not resp.headers["Via"]:
                    raise "Error"
                print("Working:", ipport)
                file = open("checked.txt", "a")
                file.write("{}\n".format(proxy))
                file.close()
            except:
                print("Not Working:", ipport)
            session.close()

        tasks = []

        loop = asyncio.get_event_loop()

        for item in proxyList:
            tasks.append(asyncio.ensure_future(is_bad_proxy("http://" + item)))

        print("Starting... \n")
        loop.run_until_complete(asyncio.wait(tasks))
        print("\n...Finished")
        loop.close()
        #print('{} - Success'.format(proxy))

else:
    pass