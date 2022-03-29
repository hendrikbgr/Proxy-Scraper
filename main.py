from requests_html import HTMLSession
import requests
import re
import csv
import json
import sys
import urllib.request, socket
from threading import Thread
import asyncio
import sys
import aiohttp
import datetime
import urllib.request, urllib.parse, urllib.error
import http.cookiejar
# Concurrency
import threading
import queue
import itertools
import tweepy

# Etc
import time
from colorama import Fore, Back, Style

version = "0.0.3"
proxy_list = []
proxy_count = 0
bad_proxy_count = 0
good_proxy_count = 0
checked_count = 0

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
            print()

        # Get Proxies
        page = r.html.find('html', first=True)
        proxies_found = re.findall('\d+\.\d+\.\d+\.\d+\:\d+', page.html)
        proxy_list = proxy_list + proxies_found
        for proxy in proxy_list:
            print('Proxy found: ', proxy)
            proxy_count += 1

        session.close()

        for link in links:

            print('Crawling Proxies from: ', link)

            try:
                r = session.get(link)
                page = r.html.find('html', first=True)
                proxies_found = re.findall('\d+\.\d+\.\d+\.\d+\:\d+', page.html)
                proxy_list = proxy_list + proxies_found
                for proxy in proxy_list:
                    proxy_count += 1
                    print('Proxy found: ', proxy)
                session.close()
            except:
                pass
    except:
        pass
    

print()
print('TOTAL NUMBER OF PROXIES CRAWLED: ', len(proxy_list))

# Save Proxies to File
proxy_list = list(dict.fromkeys(proxy_list))
with open('proxies.txt', mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join(proxy_list))

print('TOTAL NUMBER AFTER DUPE REMOVE: ', len(proxy_list))
print()
print()
print()

# Check Proxies


print('--------------------------------------')
print('- Easy Proxy Scraper & Checker {} -'.format(version))
print('- Found {} Proxies to Check         -'.format(len(proxy_list)))
print('--------------------------------------')
print()
print()



# Global variables
in_filename  = 'proxies.txt'
#in_directory = './'
out_filename = 'checked.txt'
test_url = 'http://www.google.com/humans.txt'
thread_number = 100
timeout_value = 10

ok_msg = Fore.GREEN + "OK!  " + Fore.RESET
fail_msg = Fore.RED + "FAIL " + Fore.RESET

# Stats
good_proxy_num = itertools.count()
start_time = time.time()
end_time   = time.time()

# Safe print()
mylock = threading.Lock()
def sprint(*a, **b):
    with mylock:
        print(*a, **b)


#
# Printer
#
class PrintThread(threading.Thread):
    def __init__(self, queue, filename):
        threading.Thread.__init__(self)
        self.queue = queue
        self.output = open(filename, 'a')
        self.shutdown = False

    def write(self, line):
        print(line, file=self.output)

    def run(self):
        while not self.shutdown:
            lines = self.queue.get()
            self.write(lines)
            self.queue.task_done()

    def terminate(self):
        self.output.close()
        self.shutdown = True



#
# Processor
#
class ProcessThread(threading.Thread):
    def __init__(self, id, task_queue, out_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.out_queue  = out_queue
        self.id = id

    # ...
    def run(self):
        while True:
            task   = self.task_queue.get()
            result = self.process(task)

            if result is not None:
                self.out_queue.put(result)
                next(good_proxy_num)

            self.task_queue.task_done()


    # Do the processing job here
    def process(self, task):
        proxy = task
        log_msg = str("Thread #%3d.  Trying HTTP proxy %21s \t\t" % (self.id, proxy))

        cj =  http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(
                    urllib.request.HTTPCookieProcessor(cj),
                    urllib.request.HTTPRedirectHandler(),
                    urllib.request.ProxyHandler({ 'http' : proxy })
        )

        try:
            t1 = time.time()
            response = opener.open(test_url, timeout=timeout_value).read()
            t2 = time.time()
        except Exception as e:
            log_msg += "%s (%s)" % (fail_msg, str(e))
            sprint(log_msg)
            return None

        log_msg += ok_msg + " Response time: %d, length=%s" % ( int((t2-t1)*1000), str(len(response)) )
        sprint(log_msg)
        return proxy

    def terminate(self):
        None
        #print("Thread #%d is down..." % (self.id))

#
# Main starts here
#
# Init some stuff
input_queue  = queue.Queue()
result_queue = queue.Queue()


# Spawn worker threads
workers = []
for i in range(0, thread_number):
    t = ProcessThread(i, input_queue, result_queue)
    t.setDaemon(True)
    t.start()
    workers.append(t)

# Spawn printer thread to print
f_printer = PrintThread(result_queue, out_filename)
f_printer.setDaemon(True)
f_printer.start()

# Add some stuff to the input queue
start_time = time.time()

import os

for proxy in proxy_list:
    input_queue.put(proxy)

total_proxy_num = len(proxy_list)
print("got %d proxies to check" % total_proxy_num)

if total_proxy_num == 0:
    exit()

# Wait for queue to get empty
input_queue.join()
result_queue.join()


#while (not input_queue.empty()):
#    time.sleep(1)


# Shutdown
f_printer.terminate()

for worker in workers:
    worker.terminate()


# Print some info
good_proxy_num = float(next(good_proxy_num))
print("In: %d. Good: %d, that's %.2f%%" % (total_proxy_num, good_proxy_num, 100.0 * good_proxy_num/total_proxy_num))

end_time = time.time()
print("Time elapsed: %.1f seconds." % (end_time - start_time))
print("Bye-bye!")


final_result = "Total Proxies Crawled: {} | Total Good Proxies: {} | Download: https://cutt.ly/Lm8Vjq8 | #freeproxies #proxylist #freeproxylist #proxies #crackingtools #proxy #freestuff".format(total_proxy_num, good_proxy_num)
print(final_result)