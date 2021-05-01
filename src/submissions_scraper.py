import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re


def extractText(element):
    return element.text.strip()


def fetch_page(username, page_number):
    headers = {
        'authority': 'www.codechef.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'sec-gpc': '1',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://www.codechef.com/users/{username}',
        'accept-language': 'en-US,en;q=0.9',
    }
    params = (
        ('page', page_number),
        ('user_handle', f'{username}'),
    )
    response = requests.get(
        'https://www.codechef.com/recent/user', headers=headers, params=params)
    return response.json()


def fetch_n_pages(username):
    return fetch_page(username, 0)["max_page"]


def fetch_all_submissions(username: str):
    n_pages = fetch_n_pages(username)
    arglist = [(username, i) for i in range(0, n_pages)]
    with ThreadPoolExecutor() as executor:
        pages = list(executor.map(lambda p: fetch_page(*p), arglist))
    submissions = []
    for page in pages:
        soup = BeautifulSoup(page["content"], "lxml")
        for tr in soup.table.select("tr")[1:]:
            tds = tr.select("td")
            points = 0
            verdict_raw = tds[2].span["title"].strip()
            if verdict_raw == "accepted" or verdict_raw == "":
                verdict = "AC"
                search_result = re.findall(r'\[(\d+)pts\]', str(tds[2]))
                if search_result:
                    points = int(search_result[0])
            elif verdict_raw == "time limit exceeded":
                verdict = "TLE"
            elif verdict_raw == "memory limit exceeded":
                verdict = "MLE"
            elif verdict_raw == "wrong answer":
                verdict = "WA"
            elif verdict_raw == "compilation error":
                verdict = "CE"
            elif verdict_raw == "internal error":
                verdict = "IE"
            elif verdict_raw.startswith("runtime error"):
                verdict = "RE"
            else:
                print(tds[2], verdict_raw)
                raise ValueError()

            submissions.append({
                "time": extractText(tds[0]),
                "problem": tds[1].a["href"],
                "problemCode": extractText(tds[1]),
                "verdict": verdict,
                "language": extractText(tds[3]),
                "pointsAwarded": points
            })
    return submissions


if __name__ == "__main__":
    print(fetch_all_submissions("practicec"))
