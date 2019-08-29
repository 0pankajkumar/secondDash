function JSONToCSVConvertor(JSONData, ReportTitle) {
  //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
  var arrData = typeof JSONData != "object" ? JSON.parse(JSONData) : JSONData;

  var CSV = "";
  //Set Report title in first row or line

  let temp =
    "Origin" +
    "," +
    "New Lead" +
    "," +
    "Reached Out" +
    "," +
    "New Applicant" +
    "," +
    "Recruiter Screen" +
    "," +
    "Phone Interview" +
    "," +
    "Onsite" +
    "," +
    "Offer";

  CSV += temp;
  CSV += "\r\n\r\n";

  for (let eachPost of arrData) {
    CSV += '"';
    CSV += eachPost["title"];
    CSV += '"\r\n';

    for (let i = 0; i < eachPost["_children"].length; i++) {
      let line = "";
      line += eachPost["_children"][i]["title"];
      line += ",";
      line += eachPost["_children"][i]["newLeadCount"];
      line += ",";
      line += eachPost["_children"][i]["reachedOutCount"];
      line += ",";
      line += eachPost["_children"][i]["newApplicantCount"];
      line += ",";
      line += eachPost["_children"][i]["recruiterScreenCount"];
      line += ",";
      line += eachPost["_children"][i]["phoneInterviewCount"];
      line += ",";
      line += eachPost["_children"][i]["onsiteInterviewCount"];
      line += ",";
      line += eachPost["_children"][i]["offerCount"];
      line += "\r\n";

      CSV += line;
    }
    CSV += "\r\n";
  }

  if (CSV == "") {
    alert("Invalid data");
    return;
  }

  //Generate a file name
  var fileName = "MyReport_";
  //this will remove the blank-spaces from the title and replace it with an underscore
  fileName += ReportTitle.replace(/ /g, "_");

  //Initialize file format you want csv or xls
  var uri = "data:text/csv;charset=utf-8," + escape(CSV);

  // Now the little tricky part.
  // you can use either>> window.open(uri);
  // but this will not work in some browsers
  // or you will not get the correct file extension

  //this trick will generate a temp <a /> tag
  var link = document.createElement("a");
  link.href = uri;

  //set the visibility hidden so it will not effect on your web-layout
  link.style = "visibility:hidden";
  link.download = fileName + ".csv";

  //this part will append the anchor tag and remove it after automatic click
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}