import requests
from bs4 import BeautifulSoup

url = 'https://thitruongnongsan.gov.vn/vn/nguonwmy.aspx'
resp = requests.get(url, timeout=30)
print('status', resp.status_code)

soup = BeautifulSoup(resp.text, 'html.parser')
form = soup.find('form', {'id': 'aspnetForm'})
print('form', form is not None)

if form:
    print('inputs')
    for inp in form.find_all('input'):
        print(inp.get('type'), inp.get('name'), repr(inp.get('value')))
    print('selects')
    for sel in form.find_all('select'):
        print(sel.get('name'))
        for opt in sel.find_all('option')[:20]:
            print('  ', repr(opt.get('value')), 'selected' if opt.has_attr('selected') else '')
