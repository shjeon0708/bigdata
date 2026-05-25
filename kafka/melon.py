import MySQLdb
import requests
from bs4 import BeautifulSoup

RANK = 100
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
req = requests.get('https://www.melon.com/chart/week/index.htm', headers=header)
soup = BeautifulSoup(req.text, 'html.parser')

titles = soup.find_all("div", {"class": "ellipsis rank01"})
singers = soup.find_all("div", {"class": "ellipsis rank02"})

items = []
for i in range(min(RANK, len(titles))):
    title = titles[i].find('a').text.strip()
    singer = singers[i].find('span', {"class": "checkEllipsis"}).text.strip()
    items.append((i + 1, title, singer))

print(f"크롤링된 곡 수: {len(items)}")

conn = MySQLdb.connect(
    user="crawl_user", passwd="Dankook1!",
    host="mysql.kafka.svc.cluster.local",
    db="crawl_db", charset="utf8")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS melon (
  id INT NOT NULL AUTO_INCREMENT,
  rank_no INT,
  title VARCHAR(255),
  singer VARCHAR(255),
  PRIMARY KEY (id)
)""")

for rank_no, title, singer in items:
    cursor.execute(
        "INSERT INTO melon (rank_no, title, singer) VALUES (%s, %s, %s)",
        (rank_no, title, singer))
conn.commit()
print(f"crawl_db.melon 에 {len(items)}건 저장 완료")
conn.close()
