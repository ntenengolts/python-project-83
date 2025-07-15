from bs4 import BeautifulSoup


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return {
        "h1": soup.find('h1').get_text(strip=True) if soup.find('h1') else None,
        "title": soup.title.string if soup.title else None,
        "description": (
            soup.find('meta', attrs={'name': 'description'})['content']
            if soup.find('meta', attrs={'name': 'description'}) else None
        )
    }
