import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

with open("students.json", "rb") as datafile:
	data = json.load(datafile)

	data = sorted(data.items())
	for item in data:
		pp.pprint(item)
		print ""