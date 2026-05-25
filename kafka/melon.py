import MySQLdb, requests
from bs4 import BeautifulSoup

RANK = 100
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
req = requests.get('https://www.melon.com/chart/week/index.htm', headers=header)
soup = BeautifulSoup(req.text, 'html.parser')
titles = soup.find_all("div", {"class": "ellipsis rank01"})
singers = soup.find_all("div", {"class": "ellipsis rank02"})

items = []
for i in range(min(RANK, len(titles))):
    t = titles[i].find('a').text.strip()
    s = singers[i].find('span', {"class": "checkEllipsis"}).text.strip()
    items.append((i + 1, t, s))
print(f"크롤링된 곡 수: {len(items)}")

conn = MySQLdb.connect(user="root", passwd="Dankook1!",
    host="mysql.kafka.svc.cluster.local", db="test", charset="utf8")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS melon (
  id INT NOT NULL AUTO_INCREMENT, rank_no INT,
  title VARCHAR(255), singer VARCHAR(255), PRIMARY KEY (id))""")
for r, t, s in items:
    cur.execute("INSERT INTO melon (rank_no, title, singer) VALUES (%s,%s,%s)", (r, t, s))
conn.commit()
print(f"test.melon 에 {len(items)}건 저장 완료")
conn.close()
