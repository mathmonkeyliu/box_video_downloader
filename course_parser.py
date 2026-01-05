import requests
from bs4 import BeautifulSoup
import re

def parse_course_page(url) -> list[dict[str, str]]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    items = []
    for dt in soup.find_all('dt'):
        # Extract title
        text = "".join([str(c) for c in dt.contents if isinstance(c, str)]).strip()
        title = re.sub(r'^[A-Za-z]+\s+\d+\s+', '', text) or text
        
        # Find video link
        for a in dt.find_all('a', string=re.compile('Video', re.IGNORECASE)):
            if not a.find_parent('dt') == dt: continue
            items.append({'title': title, 'url': a.get('href')})
            break
            
    return items
