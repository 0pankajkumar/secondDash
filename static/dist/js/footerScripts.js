// Code to Expand & Collapse All the postings
var actionWord = "Collapse";
function findChildren(row, action) {
    if (action == "Expand"){
        row.treeExpand();
    }else{
        row.treeCollapse()};

    var childRows = row.getTreeChildren();

    if (childRows.length > 0){
        childRows.forEach(function(child){
            if (child.getTreeChildren().length > 0){
                findChildren(child, action)
            }
        })
    }
}

function traverseRows() {
    actionWord = actionWord=="Expand" ? "Collapse" : "Expand";
    document.getElementById('toggleCollapse').innerHTML = actionWord=="Expand" ? "Collapse" : "Expand";
    
    console.log(elem.value);
    var tblRows = table.getRows();
    console.log(tblRows);
    tblRows.forEach(function(row){
        if (row.getTreeChildren().length > 0){
            findChildren(row, actionWord)
        }
    });
}








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

////////////////////////////////////////////////////////////////////////
///////////////////////// For PDF download ////////////////////////////
///////////////////////////////////////////////////////////////////////
// Inspired from https://codepen.io/someatoms/pen/adojWy?editors=1010
// https://codebun.com/create-dynamic-table-using-jquery/
// And a noble person who suggested to directly print html table without getting confused with any frameworks
function createPDF(ReportTitle) {
  var sTable = document.getElementById("tableDiv").innerHTML;

  var style = "<style>";
  style = style + "table {width: 100%;font: 17px Calibri;}";
  style =
    style + "table, th, td {border: solid 1px #DDD; border-collapse: collapse;";
  style = style + "padding: 2px 3px;text-align: center;}";
  style = style + "</style>";

  // CREATE A WINDOW OBJECT.
  var win = window.open("", "", "height=700,width=700");

  win.document.write("<html><head>");
  win.document.write("<title>TAT Report</title>"); // <title> FOR PDF HEADER.
  win.document.write(style); // ADD STYLE INSIDE THE HEAD TAG.
  win.document.write("</head>");
  win.document.write("<body>");
  win.document.write(sTable); // THE TABLE CONTENTS INSIDE THE BODY TAG.
  win.document.write("</body></html>");

  win.document.close(); // CLOSE THE CURRENT WINDOW.

  win.print(); // PRINT THE CONTENTS.
}

function JSONToPDFConvertor(JSONData, ReportTitle) {
  let data = JSONData;
  var table_body = '<table border="1">';
  table_body +=
    "<thead><tr><td>Origin</td><td>New Lead</td><td>Reached Out</td><td>New Apllicant</td><td>Recruiter Screen</td><td>Phone interview</td><td>Onsite</td><td>Offer</td></tr></thead>";

  table_body += "<tbody>";

  for (let eachPost of data) {
    let temp = eachPost["title"];
    table_body += '<td colspan="8">';
    table_body += temp;
    table_body += "</td>";
    table_body += "";

    let newLeadSum = 0,
      reachedOutSum = 0,
      newApplicantSum = 0,
      recruiterScreenSum = 0,
      phoneInterviewSum = 0,
      onsiteInterviewSum = 0,
      offerSum = 0;

    for (let i = 0; i < eachPost["_children"].length; i++) {
      newLeadSum += parseInt(eachPost["_children"][i]["newLeadCount"]);
      reachedOutSum += parseInt(eachPost["_children"][i]["reachedOutCount"]);
      newApplicantSum += eachPost["_children"][i]["newApplicantCount"];
      recruiterScreenSum += eachPost["_children"][i]["recruiterScreenCount"];
      phoneInterviewSum += eachPost["_children"][i]["phoneInterviewCount"];
      onsiteInterviewSum += eachPost["_children"][i]["onsiteInterviewCount"];
      offerSum += eachPost["_children"][i]["offerCount"];

      table_body += "<tr>";
      table_body += "<td>";
      table_body += eachPost["_children"][i]["title"];
      table_body += "</td>";

      table_body += "<td>";
      table_body += eachPost["_children"][i]["newLeadCount"];
      table_body += "</td>";

      table_body += "<td>";
      table_body += eachPost["_children"][i]["reachedOutCount"];
      table_body += "</td>";

      table_body += "<td>";
      table_body += eachPost["_children"][i]["newApplicantCount"];
      table_body += "</td>";

      table_body += "<td>";
      table_body += eachPost["_children"][i]["recruiterScreenCount"];
      table_body += "</td>";

      table_body += "<td>";
      table_body += eachPost["_children"][i]["phoneInterviewCount"];
      table_body += "</td>";

      table_body += "<td>";
      table_body += eachPost["_children"][i]["onsiteInterviewCount"];
      table_body += "</td>";

      table_body += "<td>";
      table_body += eachPost["_children"][i]["offerCount"];
      table_body += "</td>";
      table_body += "</tr>";
    }

    table_body += "<tr>";
    table_body += "<td>";
    table_body += "Total";
    table_body += "</td>";

    table_body += "<td>";
    table_body += newLeadSum;
    table_body += "</td>";

    table_body += "<td>";
    table_body += reachedOutSum;
    table_body += "</td>";

    table_body += "<td>";
    table_body += newApplicantSum;
    table_body += "</td>";

    table_body += "<td>";
    table_body += recruiterScreenSum;
    table_body += "</td>";

    table_body += "<td>";
    table_body += phoneInterviewSum;
    table_body += "</td>";

    table_body += "<td>";
    table_body += onsiteInterviewSum;
    table_body += "</td>";

    table_body += "<td>";
    table_body += offerSum;
    table_body += "</td>";
    table_body += "</tr>";

    /* Adding a space in the end */
    table_body += '<tr><td colspan="8">&nbsp</td></tr>';
  }

  table_body += "</tbody></table>";
  $("#tableDiv").html(table_body);

  // Trigger the PDF download
  createPDF(ReportTitle);
}
