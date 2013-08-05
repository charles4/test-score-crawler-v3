import xlrd
import json
import time

def write_row(long_year, year, sheet, row_index, data):
	name = str(sheet.cell(row_index, 9).value) + ", " + str(sheet.cell(row_index, 10).value)
	name = name.upper()
	grade = int(sheet.cell(row_index, 12).value)
	grade = long_year+str(grade)

	score_title = sheet.cell(row_index, 32).value 
	score = sheet.cell(row_index, 36).value

	is_fay = sheet.cell(row_index, 22).value
	is_bot25_py = sheet.cell(row_index, 37).value
	is_bot25_cy = sheet.cell(row_index, 39).value

	student = {}
	student["name"] = name
	student["lastname"] = sheet.cell(row_index, 9).value.upper()
	student["firstname"] = sheet.cell(row_index, 10).value.upper()
	student["initial"] = sheet.cell(row_index, 11).value.upper()

	student['scores'] = {}
	student['scores'][grade] = {}

	student['scores'][grade][year + score_title] = score
	student['scores'][grade][year + "FAY"] = is_fay
	student['scores'][grade][year + "PY_bottom_25"] = is_bot25_py
	student['scores'][grade][year + "CY_bottom_25"] = is_bot25_cy

	if name in data:
		print "[aims] found %s" % data[name]
		if grade in data[name]['scores']:
			data[name]['scores'][grade][year + score_title] = score
			data[name]['scores'][grade][year + "FAY"] = is_fay
			data[name]['scores'][grade][year + "PY_bottom_25"] = is_bot25_py
			data[name]['scores'][grade][year + "CY_bottom_25"] = is_bot25_cy
		else:
			data[name]['scores'][grade] = {}
			data[name]['scores'][grade][year + score_title] = score
			data[name]['scores'][grade][year + "FAY"] = is_fay
			data[name]['scores'][grade][year + "PY_bottom_25"] = is_bot25_py
			data[name]['scores'][grade][year + "CY_bottom_25"] = is_bot25_cy
		print "[aims] updated to %s " % data[name]
		print ""
	else:
		data[name] = student
		print "[aims] created %s" % data[name]
		print ""


def parse(output_filename):

	with open(output_filename, 'rb') as datafile:

		data = json.load(datafile)

		book = xlrd.open_workbook("aims_data/2012.xls")
		sheet = book.sheet_by_index(0)

		for row_index in range(1, sheet.nrows):
			write_row(long_year="2011-2012", year="2011", sheet=sheet, row_index=row_index, data=data)


		book = xlrd.open_workbook("aims_data/2013.xls")
		sheet = book.sheet_by_index(0)

		for row_index in range(1, sheet.nrows):
			write_row(long_year="2012-2013", year="2012", sheet=sheet, row_index=row_index, data=data)

	with open(output_filename, 'wb') as datafile:
		json.dump(data, datafile)


if __name__ == "__main__":
	parse("students.json")
