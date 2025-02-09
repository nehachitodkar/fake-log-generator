#!/usr/bin/python
import argparse
import datetime
import random
import sys
import time

import numpy as np
from faker import Faker
from tzlocal import get_localzone

import log_write_sleep

local = get_localzone()

# Argument parser
parser = argparse.ArgumentParser(__file__, description="Fake Apache and Nginx Log Generator")
parser.add_argument("--num", "-n", dest='num_lines', help="Number of lines to generate (0 for infinite)", type=int, default=1)
parser.add_argument("--sleep", "-s", help="Sleep this long between lines (in seconds)", default=0.0, type=float)
parser.add_argument("--min-delay", help="Minimum delay between writes in milliseconds", default=0, type=int)
parser.add_argument("--max-delay", help="Maximum delay between writes in milliseconds", default=0, type=int)
parser.add_argument("--log-type", "-t", dest='log_type', help="Type of log to generate", choices=['APACHE', 'NGINX'], default='APACHE')

args = parser.parse_args()

log_lines = args.num_lines
min_write_delay = args.min_delay
max_write_delay = args.max_delay
log_type = args.log_type
faker = Faker()

# Determine appropriate log file path
if log_type == 'APACHE':
    log_file_path = "/var/log/apache2/access.log"
elif log_type == 'NGINX':
    log_file_path = "/var/log/nginx/access.log"
else:
    print("Invalid log type specified.")
    sys.exit(1)

response = ["200", "404", "500", "301"]
verb = ["GET", "POST", "DELETE", "PUT"]
resources = ["/list", "/wp-content", "/wp-admin", "/explore", "/search/tag/list", "/app/main/posts", "/posts/posts/explore", "/apps/cart.jsp?appID="]
ualist = [faker.firefox, faker.chrome, faker.safari, faker.internet_explorer, faker.opera]

rng = np.random.default_rng(seed=int(time.time()))

flag = True
while flag:
    write_sleep = log_write_sleep.write_sleep(min_write_delay, max_write_delay)
    if write_sleep != 0:
        time.sleep(write_sleep / 1000)
    
    if args.sleep:
        increment = datetime.timedelta(seconds=args.sleep)
    else:
        increment = datetime.timedelta(seconds=random.randint(30, 300))
    
    otime = datetime.datetime.now()
    ip = faker.ipv4()
    dt = otime.strftime('%d/%b/%Y:%H:%M:%S')
    tz = datetime.datetime.now(local).strftime('%z')
    vrb = rng.choice(verb, p=[0.6, 0.1, 0.1, 0.2])
    uri = random.choice(resources)
    if "apps" in uri:
        uri += repr(random.randint(1000, 10000))
    resp = rng.choice(response, p=[0.9, 0.04, 0.02, 0.04])
    byt = int(random.gauss(5000, 50))
    referer = faker.uri()
    useragent = rng.choice(ualist, p=[0.5, 0.3, 0.1, 0.05, 0.05])()
    
    if log_type == 'APACHE':
        log_entry = f'{ip} - - [{dt} {tz}] "{vrb} {uri} HTTP/1.0" {resp} {byt} "{referer}" "{useragent}"\n'
    elif log_type == 'NGINX':
        log_entry = f'{ip} - - [{dt} {tz}] "{vrb} {uri} HTTP/1.1" {resp} {byt} "{referer}" "{useragent}"\n'
    
    # Print log entry on console
    print(log_entry, end='')
    
    # Append log entry directly to web server log file
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry)
    
    log_lines -= 1
    flag = log_lines != 0
    
    if args.sleep:
        time.sleep(args.sleep)
