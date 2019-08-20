import csv
import codecs
import shutil

# if '\0' in open('leverDump_19Aug2019_2.csv', encoding="utf8").read():
#     print("you have null bytes in your input file")
# else:
#     print("you don't")


# def fix_nulls(s):
#     for line in s:
#         yield line.replace('\0', ' ')

# r = csv.reader(fix_nulls(open('leverDump_19Aug2019_2.csv', encoding="utf8")))




# f=codecs.open('leverDump_19Aug2019_2.csv',"rb","utf-16")
# csvread=csv.reader(f,delimiter=',')
# csvread.next()
# good = 0
# for row in csvread:
#     good += 1

# print(good)





with codecs.open ('leverDump_19Aug2019_2.csv', 'rb', 'utf-8') as myfile:
    data = myfile.read()
    # clean file first if dirty
    if data.count( '\x00' ):
        print('Cleaning...')
        with codecs.open('my.csv.tmp', 'w', 'utf-8') as of:
            for line in data:
                of.write(line.replace('\x00', ''))

        shutil.move( 'my.csv.tmp', 'leverDump_19Aug2019_2_1.csv' )

# with codecs.open ('leverDump_19Aug2019_2_1.csv', 'rb', 'utf-8') as myfile:
#     myreader = csv.reader(myfile, delimiter=',')
    # Continue with your business logic here...