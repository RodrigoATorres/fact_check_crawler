#!/bin/bash
cd /usr/app/
wget $HEALTH_CHECK_URL_BASH -T 10 -t 5 -O /dev/null
scrapy runspider fact_check_crawler/spiders/boatosorg.py
