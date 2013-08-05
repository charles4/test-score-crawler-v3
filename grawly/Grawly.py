import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
import re
import json


class Grawly(object):
	""" A Galileo Crawler """

	def __init__(self, filename):
		""" When initialized, logs into galileo, selects the available year ranges"""
		self.start_time = time.time()
		self.driver = webdriver.Firefox()
		self.filename = filename

		self.login()
		self.availabe_years = self.get_available_years()
		print "available years: " + str(self.availabe_years)
		self.target_year = None
		self.target_grade = None
		self.available_grades = self.setup_grades()
		print "available grades: " + str(self.available_grades)

	def setup_grades(self):
		grades = {}
		for year in self.availabe_years:
			grades[year+":"+"0"] = False
			grades[year+":"+"1"] = False
			grades[year+":"+"2"] = False
			grades[year+":"+"3"] = False
			grades[year+":"+"4"] = False
			grades[year+":"+"5"] = False
			grades[year+":"+"6"] = False
			grades[year+":"+"7"] = False
			grades[year+":"+"8"] = False
			grades[year+":"+"9"] = False

		return grades

	def custom_loader(self, id_string):
		count = 0
		loading = True
		while loading:
			try:
				count += 1
				web_object = self.driver.find_element_by_id(id_string)
				loading = False
			except NoSuchElementException:
				if count > 5:
					print "Could not find %s. Giving up after %d trys." % (id_string, count)
					return None
				loading = True
				print "Could not find %s. Retrying. Count = %d" % (id_string, count)
				pass

		return web_object

	def custom_xpath_loader(self, xpath):
		count = 0
		loading = True
		while loading:
			count += 1
			web_object_list = self.driver.find_elements_by_xpath(xpath)
			loading = False
			
			### web object list is None
			if not web_object_list:
				if count > 5:
					print "Could not find %s. Giving up after %d trys." % (xpath, count)
					return None
				loading = True
				print "Could not find %s. Retrying. Count = %d" % (xpath, count)
				pass

		return web_object_list

	def login(self):
		### sign in
		self.driver.get("https://www.assessmenttechnology.com/GalileoASP/ASPX/K12Login.aspx")

		emailid=self.custom_loader("txtUsername")
		emailid.send_keys("mcosta@scstucson.org")


		passw=self.custom_loader("txtPassword")
		passw.send_keys("galileo")

		signin=self.custom_loader("btnLogin")
		signin.click()

	def get_available_years(self):
		years = []
		self.driver.get("https://www.assessmenttechnology.com/GalileoASP/ASPX/User/UserSettings.aspx")

		year_drop_down = self.custom_loader("ddlProgramYear")
		options = year_drop_down.find_elements_by_tag_name("option")
		for option in options:
			years.append(option.text)

		return years

	def set_year_on_galileo(self):
		self.driver.get("https://www.assessmenttechnology.com/GalileoASP/ASPX/User/UserSettings.aspx")

		year_drop_down = self.custom_loader("ddlProgramYear")
		options = year_drop_down.find_elements_by_tag_name("option")
		for option in options:
			if option.text == self.target_year:
				option.click()
				### break because the options object goes stale after the click
				break

		save_btn = self.custom_loader("btnSaveYearAndTerm")

		save_btn.click()

	def crawl(self):
		try:
			for year in self.availabe_years:
				self.target_year = year
				self.set_year_on_galileo()

				self.crawl_target_year()

		finally:
			self.driver.quit()

	def determine_numeric_grade_from_string(self, _string):
		grades = [ int(s) for s in re.findall(r'\d+', _string)]

		if "Algebra" in _string:
			return 9
		elif "Bechtold" in _string:
			return None
		elif "english" in _string or "English" in _string:
			return None
		elif "KG" in _string:
			return 0 # kindergarden
		elif "K" in _string.split("_"):
			return 0
		elif len(grades) == 0 :
			return None
		else:
			return grades[0]

	def select_class_dropdown(self):
		### upsettingly sometimes the dropdown is called "ClassPicker_cboClass" and sometimes "ClassPicker$cboClass"
		class_dropdown = self.custom_loader("ClassPicker_cboClass")
		if class_dropdown is None:
			class_dropdown = self.custom_loader("ClassPicker$cboClass", driver)

		return class_dropdown

	def crawl_target_year(self):
		self.driver.get("https://www.assessmenttechnology.com/GalileoASP/ASPX/Testing/BenchmarkResults/ClassBenchmarkResults.aspx")

		class_dropdown = self.select_class_dropdown()

		### determine number of classes
		classes = []
		for option in class_dropdown.find_elements_by_tag_name("option"):
			classes.append(option.text)

		print "Num of classes = ", len(classes)
		i = 0

		### only need to visit one class from each grade
		for grade in self.available_grades.keys():
			self.target_grade = grade
			for target_class in classes:
				class_option_grade = self.determine_numeric_grade_from_string( target_class )
				grade_int_value = int(grade.split(":")[1])
				grade_year = grade.split(":")[0]
				if  class_option_grade == grade_int_value and self.target_year == grade_year:
					### check if grade has been visited or not
					if self.available_grades[grade] == False:
						self.crawl_target_class( target_class )
						self.available_grades[grade] = True

	def crawl_target_class(self, target_class):
		print "Crawling ", self.target_year, target_class

		### select class dropdown
		class_dropdown = self.select_class_dropdown()

		for class_option in class_dropdown.find_elements_by_tag_name("option"):
			if class_option.text == target_class:
				### page refreshes on click
				### break to loop to avoid expired items
				class_option.click()
				break

		### page has refreshed
		library_dropdown = self.custom_loader("cboLibraries")
		librarys = []
		for library_option in library_dropdown.find_elements_by_tag_name("option"):
			librarys.append(library_option.text)

		### visit each library
		for library in librarys:
			self.crawl_target_library(library)

	def crawl_target_library(self, target_library):
		print "Crawling ", self.target_year, target_library

		library_dropdown = self.custom_loader("cboLibraries")

		for library_option in library_dropdown.find_elements_by_tag_name("option"):
			if library_option.text == target_library:
				library_option.click()
				break

		### page has refreshed
		subject_dropdown = self.custom_loader("ddlSubjects")
		subjects = []

		for subject_option in subject_dropdown.find_elements_by_tag_name("option"):
			subjects.append(subject_option.text)

		### visit each subject
		for subject in subjects:
			target_grade = int(self.target_grade.split(":")[1])
			subject_grade = self.determine_numeric_grade_from_string(subject)
			if target_grade == subject_grade:
				self.crawl_target_subject(subject)

	def add_scores_to_student(self, student, cols, col_names):
		for col in cols[1:]:
			col_index = cols.index(col)
			col_name = col_names[col_index].replace(".", "")
			col_name = col_name.split("\n")[0]
			if "Risk Assessment" in col_name:
				prev_colname = col_names[cols.index(col)-1].replace(".", "").split("\n")[0]
				col_name = "Risk Assessment:" + prev_colname
			student['scores'][self.target_grade][col_name] = col.text

	def crawl_target_subject(self, target_subject):

		print "Crawling ", self.target_year, self.target_grade, target_subject

		subject_dropdown = self.custom_loader("ddlSubjects")

		for subject_option in subject_dropdown.find_elements_by_tag_name("option"):
			if subject_option.text == target_subject:
				subject_option.click()
				break

		### page has refreshed
		### read information
		try:
			### open existing student information
			with open(self.filename, 'rb') as datafile:
				data = json.load(datafile)
				result_table = self.custom_loader("tableResults")
				result_table_rows = result_table.find_elements_by_tag_name("tr")

				col_names = []
				for col in result_table_rows[0].find_elements_by_tag_name("td"):
					col_names.append(col.text)

				### skipping first row
				for row in result_table_rows[1:]:
					cols = row.find_elements_by_tag_name("td")
					student_name = cols[0].text
					student_name = student_name.upper()


					student = {}
					student["lastname"] = student_name.split(",")[0]
					student["firstname"] = student_name.split(",")[1].strip(" ").split(" ")[0]
					try:
						student["initial"] = student_name.split(",")[1].strip(" ").split(" ")[1]
					except Exception, e:
						student["initial"] = None
					student['name'] = student["lastname"] + ", " + student['firstname']
					student_name = student['name']

					student['scores'] = {}
					student['scores'][self.target_grade] = {}

					self.add_scores_to_student(student=student, cols=cols, col_names=col_names)
						
					### check if student exists already in datafile
					### if he/she does append more scores
					name = student_name
					grade = self.target_grade
					if name in data:
						print "[galileo] found %s" % data[name]
						if grade in data[name]['scores']:
							self.add_scores_to_student(student=data[name], cols=cols, col_names=col_names)
						else:
							data[name]['scores'][grade] = {}
							self.add_scores_to_student(student=data[name], cols=cols, col_names=col_names)
						print "[galileo] updated to %s " % data[name]
						print ""
					else:
						data[name] = student
						print "[galileo] created %s" % data[name]
						print ""

			### dump data into json file
			with open(self.filename, 'wb') as datafile:
				json.dump(data, datafile)


		except Exception, e:
			print "Error, " , e

if __name__ == "__main__":
	grawler = Grawly("students.json")
	grawler.crawl()
