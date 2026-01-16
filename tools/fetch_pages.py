import sys
from pathlib import Path
import urllib.request

BASE = 'http://127.0.0.1:8000'
quotes = [4]
for q in quotes:
    for path in [f'/quotations/{q}/', f'/quotations/{q}/performa/create/']:
        url = BASE + path
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                html = r.read().decode('utf-8', errors='ignore')
                print('\n---', url, '---\n')
                print(html[:800])
        except Exception as e:
            print('ERROR fetching', url, e)
