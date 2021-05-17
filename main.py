from requests_html import HTMLSession
import url_config
import requests
import re
import csv
import json

proxy_list = []
proxy_count = 0

for url in url_config.urls:
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