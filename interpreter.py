import json
import xlwt
from datetime import date
import os
import re


class Converter(object):

	def __init__(self, fay_only=True):
		with open("students.json", "rb") as datafile:
			data = json.load(datafile)
			self.data = data

		self.fay_only = fay_only

		self.wb = xlwt.Workbook()
		self.ws_all = self.wb.add_sheet('all students')
		self.ws_bot25 = self.wb.add_sheet('bot25')
		self.ws_kinder = self.wb.add_sheet('Kinder')
		self.ws_first = self.wb.add_sheet('First')
		self.ws_second = self.wb.add_sheet('Second')
		self.ws_third = self.wb.add_sheet('Third')
		self.ws_fourth = self.wb.add_sheet("Fourth")
		self.ws_fifth = self.wb.add_sheet("Fifth")
		self.ws_sixth = self.wb.add_sheet("Sixth")
		self.ws_seventh = self.wb.add_sheet("Seventh")
		self.ws_eighth = self.wb.add_sheet("Eighth")
		self.ws_nineth = self.wb.add_sheet("Nineth")
		self.ws_array = [self.ws_kinder, self.ws_first, self.ws_second, self.ws_third, self.ws_fourth, self.ws_fifth, self.ws_sixth, self.ws_seventh, self.ws_eighth, self.ws_nineth]

		self.schoolyear = self.get_schoolyear()

	def get_schoolyear(self):
		""" returns schoolyear aka 2011-2012 or 2012-2013 """
		d = date.today()

		if d.month < 9:
			year = d.year
			lastyear = year - 1
		else:
			year = d.year + 1
			lastyear = d.year

		schoolyear = str(lastyear) + "-" + str(year)
		return schoolyear

	def get_students_from_this_year(self, target_grade=None):
		""" returns list of tuples ( grade, studentname ) """
		students = []
		for student in self.data:
			for yeargrade in self.data[student]['scores']:
				schoolyear, grade = yeargrade.split(":")
				if target_grade == None:
					if self.schoolyear == schoolyear:
						if self.fay_only:
							try:
								if int(self.data[student]['scores'][yeargrade]["FAY"]) == 1 or int(grade) < 3:
									students.append((grade, student))
							except KeyError:
								pass
						else:
							students.append((grade, student))
				else:
					if target_grade == int(grade) and self.schoolyear == schoolyear:
						if self.fay_only:
							try:
								if int(self.data[student]['scores'][yeargrade]["FAY"]) == 1 or int(grade) < 3:
									students.append((grade, student))
							except KeyError:
								pass
						else:
							students.append((grade, student))


		return students

	def fill_all_worksheet(self):
		""" fill the all students worksheet """
		students = sorted(self.get_students_from_this_year())
		for student in students:
			self.ws_all.write(students.index(student), 0, student[1])
			self.ws_all.write(students.index(student), 1, student[0])

	def fill_grade_worksheet(self, grade):
		""" fill worksheet specfic to a grade """
		students = sorted(self.get_students_from_this_year(target_grade=grade))
		student_names = []
		for s in students:
			student_names.append(s[1])
		score_titles = ["student name"] + self.get_score_title_set(student_names)
		target_ws = self.ws_array[grade]

		### write to ws
		### first top row
		for title in score_titles:
			target_ws.write(0, score_titles.index(title), title)

		### now other rows, 1 per students
		for student in student_names:
			s_index = student_names.index(student) + 1
			for title in score_titles:
				if title == "student name":
					target_ws.write(s_index, score_titles.index(title), student)
				else:
					for gradeyear in self.data[student]['scores']:
						if title in self.data[student]['scores'][gradeyear]:
							try:
								target_ws.write(s_index, score_titles.index(title), self.data[student]['scores'][gradeyear][title])
							except:
								print student, 'scores', title, self.data[student]['scores'][gradeyear][title]
								print "tried to overwrite."
	def save_excel_file(self):
		""" saves the excel file to disk """
		d = date.today()
		report_name = 'report_%s_#1.xls' % (d)
		PATH = "/reports"

		count = 0
		for dirname, dirnames, filenames in os.walk(PATH):
			for filename in filenames:
				if filename == report_name:
					count += 1
				if re.match(r'report_%s(\w+)' % (d), filename):
					count += 1 

		if count > 0:
			report_name = 'report_%s_#%d.xls' % (d, count+1)

		self.wb.save(os.path.join(PATH, report_name))

	def get_score_title_set(self, students):
		""" returns a set of all score titles from a set of students """
		titles = []
		for student in students:
			for yeargrade in self.data[student]['scores']:
				year, grade = yeargrade.split(":")
				for score_title in self.data[student]['scores'][yeargrade]:
					titles.append(score_title)

		return sorted(set(titles))


if __name__ == "__main__":
	c = Converter(fay_only=False)
	c.fill_all_worksheet()
	for i in range(10):
		c.fill_grade_worksheet(grade=i)
	c.save_excel_file()

