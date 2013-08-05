from __future__ import with_statement
import time
import mechanize
import csv
from datetime import date
import json




class Drawly(object):

	def __init__(self, datafile):
		self.start_time = time.time()
		self.br = mechanize.Browser()
		self.br.set_handle_robots( False )
		self.datafile = datafile

	def determine_grade(self, a_dictionary, year):
		ad = a_dictionary
		if ad["Year_6th"] == str(year):
			return ad["Year_6th"] + "-" + str(year+1) + ":6"
		if ad["Year_5th"] == str(year):
			return ad["Year_5th"] + "-" + str(year+1) + ":5"
		if ad["Year_4th"] == str(year):
			return ad["Year_4th"] + "-" + str(year+1) + ":4"
		if ad["Year_3rd"] == str(year):
			return ad["Year_3rd"] + "-" + str(year+1) + ":3"
		if ad["Year_2nd"] == str(year):
			return ad["Year_2nd"] + "-" + str(year+1) + ":2"
		if ad["Year_1st"] == str(year):
			return ad["Year_1st"] + "-" + str(year+1) + ":1"
		if ad["Year_K"] == str(year):
			return ad["Year_K"] + "-" + str(year+1) + ":0"

	def browse(self):

		self.br.open("https://dibels.uoregon.edu/")

		self.br.select_form("login")

		self.br["name"] = "chavez4th"
		self.br["password"] = "dibels4th"

		response = self.br.submit()

		try:
			self.br.open("https://dibels.uoregon.edu/district/welcome/skipassessmentschedule")
		except Exception, e:
			pass

		### get last year
		### 2012 is 2012-13
		d = date.today()
		year = d.year - 1

		### start year and end year are the same
		### aka the school year 2012-13 is just 2012, 2012
		self.br.open("https://dibels.uoregon.edu/reports/report.php?report=DataFarming&Scope=District&district=572&Grade=_ALL_&StartYear=%s&EndYear=%s&Assessment=10000&AssessmentPeriod=_ALL_&StudentFilter=none&Fields[]=&Fields[]=1&Fields[]=41&Delimiter=0" % (year, year))

		response = self.br.response()
		download_link = self.br.links(text_regex="Download Full Dataset")

		csv_file = self.br.retrieve(download_link.next().absolute_url)[0]

		self.read_csv_file(csv_file, year)

		### get prev year
		year = year - 1
		self.br.open("https://dibels.uoregon.edu/reports/report.php?report=DataFarming&Scope=District&district=572&Grade=_ALL_&StartYear=%s&EndYear=%s&Assessment=10000&AssessmentPeriod=_ALL_&StudentFilter=none&Fields[]=&Fields[]=1&Fields[]=41&Delimiter=0" % (year, year))

		response = self.br.response()
		download_link = self.br.links(text_regex="Download Full Dataset")

		csv_file = self.br.retrieve(download_link.next().absolute_url)[0]

		self.read_csv_file(csv_file, year)

	def read_csv_file(self, csv_file, year):

		with open(csv_file, 'rb') as csvfile:
			### open existing student information
			with open(self.datafile, 'rb') as datafile:
				data = json.load(datafile)
				for row in csv.DictReader(csvfile):
					student = {}
					grade = self.determine_grade(row, year)
					name = row["Last"] + ", " + row["First"]
					name = name.upper()

					student["name"] = name
					student["firstname"] = row["First"].upper()
					student["lastname"] = row["Last"].upper()
					student["initial"] = None

					student['scores'] = {}
					student['scores'][grade] = {}

					for key in row.keys():
						if row[key] != "":
							if key != "First" and key != "Last":
								student['scores'][grade][key] = row[key]
						
					### check if student exists already in datafile
					### if he/she does append more scores
					if name in data:
						print "[dibels] found %s" % data[name]
						if grade in data[name]['scores']:
							for key in row.keys():
								if row[key] != "":
									if key != "First" and key != "Last":
										data[name]['scores'][grade][key] = row[key]
						else:
							data[name]['scores'][grade] = {}
							for key in row.keys():
								if row[key] != "":
									if key != "First" and key != "Last":
										data[name]['scores'][grade][key] = row[key]
						print "[dibels] updated to %s " % data[name]
						print ""
					else:
						data[name] = student
						print "[dibels] created %s" % data[name]
						print ""

			### dump data into json file
			with open(self.datafile, 'wb') as datafile:
				json.dump(data, datafile)


if __name__ == "__main__":
	drawly = Drawly("students.json")
	drawly.browse()


