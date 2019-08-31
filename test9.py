import csv 

file_to_open = 'C:\\Users\\pankaj.kum\\Desktop\\d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (12).csv'

corrected_file = 'C:\\Users\\pankaj.kum\\Desktop\\d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (12) corrected.csv'

# with open(str(file_to_open), 'rb', encoding="utf8" ) as csvfile:

# with open(str(file_to_open), 'rb') as csvfile:
# 	myReader = csv.reader(csvfile, delimiter=',')
# 	for row in myReader:
# 		for col in row:
# 			if col == '\x00':
# 				print("Yeah")
		# print(row)
		# break


# data = open(file_to_open, 'rb').read()
# print(data.find(b'\x00'))

# The correcting code for Null found in csv
fi = open(file_to_open, 'rb')
data = fi.read()
fi.close()
fo = open(file_to_open, 'wb')
fo.write(data.replace(b'\x00', b''))
fo.close()