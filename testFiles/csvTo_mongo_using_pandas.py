import pandas as pd 
# Read data from file 'filename.csv' 
# (in the same directory that your python process is based)
# Control delimiters, rows, column names with read_csv (see later) 
data = pd.read_csv("d4871e75-7fb1-4176-bfa0-c3d061757298.candidates.presence.latest (4).csv", encoding="utf8", dtype={}) 
# Preview the first 5 lines of the loaded data 
data.head()