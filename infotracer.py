import csv

def pathmapping(folder,parameter,recursive,lastint):
	def intsort(elem):
		startnum = elem.rfind('_')+1
		endnum = elem.rfind('.')
		elem = int(elem[startnum:endnum])
		return elem
	import glob
	files = glob.glob(folder + parameter, recursive=recursive)
	if lastint:
		files = sorted(files, key=intsort)
	else:
		files.sort()
	return enumerate(files)

def pdftojpg(pdfs):
	import csv
	from os import system
	from pdf2image import convert_from_path

	with open('pdf2jpg_done.csv', 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',quotechar='"')
		for i, pdf in pdfs:
			print('Converting ', pdf)
			dotposition = pdf.rfind('.')
			folder = 'docclass/' + pdf[0:dotposition]
			folder = folder.replace(' ','1+')
			folder = folder.replace('(','2+')
			folder = folder.replace(')','3+')
			folder = folder.replace('\'','4+')
			folder = folder.replace('&','5+')
			system ('mkdir -p ' + folder)
			print('.')

			pages = convert_from_path(pdf, 100)
			for n, page in enumerate(pages):
				saveimgpath = folder + '/' + str(i) + '_' + str(n) + '.jpg'
				page.save(saveimgpath, 'JPEG')
			filewriter.writerow([i,pdf])
			print('done')

def cropimage(folder,img,x1,y1,x2,y2,save_pattern):
	from PIL import Image
	from os import system
	slashposition = img.rfind('/')
	jpg_name = img[slashposition+1:]
	save_jpg = folder + 'croped/' + save_pattern + jpg_name
	system ('mkdir -p ' + folder + 'croped')
	img = Image.open(img)
	crop_img = img.crop((x1, y1, x2, y2))
	crop_img.save(save_jpg)

def makevals(ul,dr):
	from os import system

	rmfolders = pathmapping('docclass/','**/croped/',True,False)
	for i,rmfolder in rmfolders:
		system('rm -r ' + rmfolder)

	folders = pathmapping('docclass/','**/',True,False)

	for i,folder in folders:
		jpgs = pathmapping(folder,'*.jpg',False,True)
		for i,jpg in jpgs:
			print(jpg)
			cropimage(folder,jpg,ul[0],ul[1],dr[0],dr[1],'croped_txt1_')
			print('.')

def GenerateReport(csv_data_import,new):
	from os import system
	if new:
		import csv
		system ('mkdir -p docclass_output')
		with open('docclass_output/report.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow(csv_data_import)
	else:
		import csv
		with open('docclass_output/report.csv', 'a') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			filewriter.writerow(csv_data_import)

def GenerateDoc(source_pdfs,folder,jpg,pages,variable_match):

	from os import system
	import re
	import pyocr
	import pyocr.builders
	from PIL import Image

	# Get input file path
	startnum = jpg.rfind('/')
	endnum = jpg.find('_',startnum)
	id_file = int(jpg[startnum+1:endnum])
	inputfile = source_pdfs[id_file]
	inputfile = inputfile[1]
	# inputpdf = PdfFileReader(open(inputfile, "rb"), strict=False)

	row_data_csv = [id_file,inputfile,pages]

	for i in range(len(variable_match)):
		cropimage(folder, jpg, variable_match[i][1][0], variable_match[i][1][1], variable_match[i][2][0], variable_match[i][2][1],'id_'+str(i))

		jpg_name = jpg[startnum+1:]
		jpg_num = folder + 'croped/' + 'id_' + str(i) + jpg_name

		# Convert image into text mode
		tools = pyocr.get_available_tools()[0]
		text = tools.image_to_string(Image.open(jpg_num), builder=pyocr.builders.DigitBuilder())

		# Generate Doc Number
		# doc_num = re.findall(r'\d+/\d+', text_num)
		doc_num = re.findall(variable_match[i][3], text)

		# if doc_num is None:
		if len(doc_num) == 0:
			doc_num = 'Not Found'

		# Saving pdf and creating report
		row_data_csv.append(doc_num)
	GenerateReport(row_data_csv, False)

def imageanalise(source_pdfs,folders,txt1,pm,variable_match):
	from fuzzywuzzy import fuzz
	from fuzzywuzzy import process
	import os
	import pyocr
	import pyocr.builders
	import re
	from PIL import Image

	# Creating a report file id_source,spath,pages,id_gen,destination,types,docid,outcome
	csv_data_import = ['ID Source','Source Path','Page'] + [i[0] for i in variable_match]
	GenerateReport(csv_data_import, True)

	# Verify subfolder in main folder
	for i, folder in folders:
		vals = pathmapping(folder,'croped/croped_txt1_*.jpg',False,True)
		fdfd = list(vals)
		
		# Check for validation images inside folder
		for numpage,val in reversed(fdfd):
			print(val)

			jpg = val.replace('croped/croped_txt1_','')

			tools = pyocr.get_available_tools()[0]
			text_txt1 = tools.image_to_string(Image.open(val), builder=pyocr.builders.DigitBuilder())
			print(text_txt1)
			print(fuzz.token_set_ratio(txt1, text_txt1))
			if fuzz.token_set_ratio(txt1, text_txt1) > pm:

				GenerateDoc(source_pdfs,folder,jpg,numpage,variable_match)
				print('\n ============ DOCUMENT FOUND =========== \n')
	
	os.system('rm -r -f docclass/')


def main():
	import re
	while True: 
		print('Press P to convert jpg2pdf | C to crop sizeble images | A to analize images')
		V = input()
		if (V=='P' or V=='p' or V=='C' or V=='c' or V=='A' or V=='a'):
			break

	if (V=='P' or V=='p'):
		while True: 
			print('Do you want to create a pdf list pdf_list.csv (Y/N)')
			S = input()
			if (S=='Y' or S=='y' or S=='N' or S=='n'):
				break
		
		while True: 
			print('Press K to keep using pdf_list.csv or C to use pdf_listt.csv')
			T = input()
			if (T=='K' or T=='k' or T=='C' or T=='c'):
				break

		if (S=='Y' or S=='y'):
			source_pdfs = pathmapping('','**/*.pdf',True,False)
			with open('pdf_list.csv', 'w') as csvfile:
				filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
				for npdf, path in source_pdfs:
					filewriter.writerow([npdf,path])
			with open('pdf2jpg_done.csv', 'w') as csvfile:
				filewriter = csv.writer(csvfile, delimiter=',',quotechar='"')
				filewriter.writerow(['ID File','File Path'])

		if (T=='C' or T=='c'):
			with open('pdf_listt.csv', 'r') as f:
				reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
				source_pdfs = list(reader)

		else:
			with open('pdf_list.csv', 'r') as f:
				reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
				source_pdfs = list(reader)

		# Convert PDF to JPG
		pdftojpg(source_pdfs)


	elif (V=='C' or V=='c'):
		# Make validation images for docs identifying
		while True:
			print('Type the x,y upper-left position of image detection [e.g. 10,20]')
			ul = input()
			if re.match(r'\d+,\d+$',ul):
				ul = list(map(int,ul.split(',')))
				break
		while True:
			print('Type the x,y down-right position of image detection [e.g. 60,70]')
			dr = input()
			if re.match(r'\d+,\d+$',dr):
				dr = list(map(int,dr.split(',')))
				break
		makevals(ul,dr)


	else:
		print('Type a word or text to be recognised on croped area of a document match')
		txt1 = input()

		while True:
			print('Type the % of match [e.g. 70]')
			pm = input()
			if pm.isdigit():
				pm = int(pm)
				if pm<=100 and pm>=0:
					break

		while True: 
			print('Type # of variables to be captured')
			n_variables = input()
			if n_variables.isdigit():
				n_variables = int(n_variables)
				break
		
		variable_match = []

		for i in range(n_variables):
			print('Type the name of variable')
			nvar = input()

			while True:
				print('Type the x,y upper-left position of variable')
				ul = input()
				if re.match(r'\d+,\d+$',ul):
					ul = list(map(int,ul.split(',')))
					break
			while True:
				print('Type the x,y down-right position of variable')
				dr = input()
				if re.match(r'\d+,\d+$',dr):
					dr = list(map(int,dr.split(',')))
					break
					
			print('Type the regex of the variable [e.g. for 02/2018 use \d+/\d+]')
			regex_variable = input()

			variable_match.append([nvar,ul,dr,regex_variable])
		
		with open('pdf_list.csv', 'r') as f:
			reader = csv.reader(f, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			source_pdfs = list(reader)


		folders = pathmapping('docclass/','**/',True,False)
		folders = list(folders)
		with open('folder_list.csv', 'w') as csvfile:
			filewriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for nfolder, folder in folders:
				filewriter.writerow([nfolder,folder])
	
		# Analise images looking for documents
		imageanalise(source_pdfs,folders,txt1,pm,variable_match)

main()
