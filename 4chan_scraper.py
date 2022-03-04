import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os

FORMATS = {"image": {"jpg", "png", "webp", "gif", "tiff"},
           "video": {"mp4", "webm", "mkv", "avi", "mov", "flv", "mpeg"},
           "all": ""
          }
URL = sys.argv[1]
if len(sys.argv) > 2:
    target_format = FORMATS[sys.argv[2]]
else:
    target_format = FORMATS["image"]


main_page = requests.get(URL)
subject = BeautifulSoup(main_page.text, 'html.parser')
subject = subject.find('span', attrs={'class': 'subject'})
subject = subject.text.translate(''.maketrans({i:'' for i in '<>:"/\|?*^'}))
path = subject + ' - ' + URL[URL.rfind('/')+1:]
os.mkdir(path)
os.chdir(path)


def get_file_list():
    r = requests.get(URL)
    result = []
    soup = BeautifulSoup(r.text, 'html.parser')
    soup = soup.findAll('div', attrs={'class': 'fileText'})
    for tag in soup:
        if any(f in tag.a.text for f in target_format):
            result.append((tag.a.text, 'https:'+tag.a.get('href')))
    return result


def worker(work):
    r = requests.get(work[1])
    with open(work[0], 'wb') as file:
        file.write(r.content)
    return 1

file_list = get_file_list()
all_files = len(file_list)
success = 0
with ThreadPoolExecutor(max_workers=5) as executor:
    to_download = {executor.submit(worker, work) for work in file_list}
    for work in as_completed(to_download):
        pass

print(all_files, 'downloaded')
