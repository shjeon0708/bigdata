import MySQLdb
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    RANK = 100  # 멜론 차트 순위가 1 ~ 100위까지 있음
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
    req = requests.get('https://www.melon.com/chart/week/index.htm',
                       headers=header)
    req.encoding = 'utf-8'   # 멜론 페이지 인코딩 명시
    html = req.text
    parse = BeautifulSoup(html, 'html.parser')
    titles = parse.find_all("div", {"class": "ellipsis rank01"})
    singers = parse.find_all("div", {"class": "ellipsis rank02"})
    title = []
    singer = []
    for t in titles:
        title.append(t.find('a').text)
    for s in singers:
        singer.append(s.find('span', {"class": "checkEllipsis"}).text)
    items = [item for item in zip(title, singer)]

    # 크롤링이 제대로 됐는지 먼저 확인 (터미널에서 한글이 보이면 크롤링은 정상)
    print(items[:5])

    conn = MySQLdb.connect(
        user="crawl_user",
        passwd="Dankook1!",
        host="10.100.111.92",
        db="crawl_db",
        charset="utf8mb4"        # 핵심 1: 연결 charset
    )
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS melon")
    cursor.execute(
        "CREATE TABLE melon ("
        "`rank` int, title text, singer text"
        ") DEFAULT CHARSET=utf8mb4")   # 핵심 2: 테이블 charset

    i = 1
    for item in items:
        cursor.execute(
            "INSERT INTO melon (`rank`, title, singer) VALUES (%s, %s, %s)",
            (i, item[0], item[1]))
        i += 1
    conn.commit()
    cursor.close()
    conn.close()
