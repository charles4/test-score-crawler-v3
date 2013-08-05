
import dibels_crawler, grawly
from aims_parser import parse
import json

### clean out old data
with open("students.json", "wb") as datafile:
	tmp = {}
	json.dump(tmp, datafile)

grawler = grawly.Grawly("students.json")
grawler.crawl()

drawler = dibels_crawler.Drawly("students.json")
drawler.browse()

parse("students.json")


