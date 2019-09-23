import os, shutil
# folder = 'C:\\Users\\pankaj.kum\\Desktop\\j\\uploads'
# folder = '/home/j/uploads'

folder = '/var/www/FlaskApp/FlaskApp/uploaded_csv'

for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)
