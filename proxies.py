import requests
from bs4 import BeautifulSoup


def get_proxies(country_name=None):
    html_doc = requests.get('https://free-proxy-list.net/').text

    soup = BeautifulSoup(html_doc, 'html.parser')

    for tr in soup.find("tbody").find_all("tr"):
        cells = tr.find_all("td")

        if country_name ==cells[3].text or country_name is None:
            yield {
                'ip': cells[0].text,
                'port': cells[1].text,
                'ipPort': f"{cells[0].text}:{cells[1].text}",
                'countryCode': cells[2].text,
                'countryName': cells[3].text
            }
