#!/bin/sh
echo 'Starting Script'
while true
do
	python3 main.py
	cd ..
	cd Free-Proxy-Repo
	git add proxy_list.txt
	git commit -m '[FPR] - Added Fresh Proxies'
	git push
	cd ..
	cd Proxy-Scraper-Raspi
	echo 'Sleeping 3 Minutes'
	sleep 1h
done
