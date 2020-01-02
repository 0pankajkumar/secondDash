import datetime, pprint

dict_to_be_written_big = [
	{
		"Posting ID" : "abcd",
		"Applied At (GMT)": datetime.datetime(2019,8,5),
		"Posting Owner Name": "abcd"
	},
	{
		"Posting ID" : "abcd",
		"Applied At (GMT)": datetime.datetime(2011,1,5),
		"Posting Owner Name": "efgh"
	},
	{
		"Posting ID" : "abcd",
		"Applied At (GMT)": datetime.datetime(2009,8,5),
		"Posting Owner Name": "ijkl"
	}
]

dict_for_actual_posting_owner = dict()

for dict_to_be_written in dict_to_be_written_big:
	# Deciding the latest or Actual "Posting Owner Name" for labelling
	if dict_to_be_written["Posting ID"] not in dict_for_actual_posting_owner:
		if isinstance(dict_to_be_written["Applied At (GMT)"], datetime.date):
			appliedDate = dict_to_be_written["Applied At (GMT)"]
		else:
			appliedDate = ""

		dict_for_actual_posting_owner[dict_to_be_written["Posting ID"]] = {
			"Actual Posting Owner Name": dict_to_be_written["Posting Owner Name"],
			"Applied At (GMT)": appliedDate
		}
	elif isinstance(dict_to_be_written["Applied At (GMT)"], datetime.date):
		if dict_for_actual_posting_owner[dict_to_be_written["Posting ID"]]["Applied At (GMT)"] > dict_to_be_written["Applied At (GMT)"]:
			print("Inside")
			dict_for_actual_posting_owner[dict_to_be_written["Posting ID"]]["Applied At (GMT)"] = dict_to_be_written["Applied At (GMT)"]
			dict_for_actual_posting_owner[dict_to_be_written["Posting ID"]]["Actual Posting Owner Name"] = dict_to_be_written["Posting Owner Name"]

pprint.pprint(dict_for_actual_posting_owner)