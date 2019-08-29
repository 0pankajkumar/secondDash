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

    let newLeadSum = 0,
      reachedOutSum = 0,
      newApplicantSum = 0,
      recruiterScreenSum = 0,
      phoneInterviewSum = 0,
      onsiteInterviewSum = 0,
      offerSum = 0;
    for (let i = 0; i < eachPost["_children"].length; i++) {
      newLeadSum += eachPost["_children"][i]["newLeadCount"];
      reachedOutSum += eachPost["_children"][i]["reachedOutCount"];
      newApplicantSum += eachPost["_children"][i]["newApplicantCount"];
      recruiterScreenSum += eachPost["_children"][i]["recruiterScreenCount"];
      phoneInterviewSum += eachPost["_children"][i]["phoneInterviewCount"];
      onsiteInterviewSum += eachPost["_children"][i]["onsiteInterviewCount"];
      offerSum += eachPost["_children"][i]["offerCount"];

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

    CSV += ",";
    CSV += newLeadSum;
    CSV += ",";
    CSV += reachedOutSum;
    CSV += ",";
    CSV += newApplicantSum;
    CSV += ",";
    CSV += recruiterScreenSum;
    CSV += ",";
    CSV += phoneInterviewSum;
    CSV += ",";
    CSV += onsiteInterviewSum;
    CSV += ",";
    CSV += offerSum;
    CSV += "\r\n";

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
