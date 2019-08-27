import csv

filepath = 'd4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (11).csv'

# with open(filepath, 'rb') as csvfile:
# 	myReader = csv.reader(csvfile, delimiter=',')
# 	for row in myReader:
# 		for r in row:
# 			if r == b'\x00':
# 				print("Null found")







# data = open(filepath, 'rb').read()
# print(data.find(b'\x00'))
# print(data.count(b'\x00'))



data = open(filepath, 'rb').read()
print(data.find(b'\x00'))
print(data.count(b'\x00'))
























