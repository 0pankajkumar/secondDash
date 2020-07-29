    // Modify title
    document.title = "Team";

    var tableUp;
    var tableLow;
    var tableUp2;
    var tableLow2;
    var tableUp3;
    var tableLow3;

    // Just for top tabs
    function openCity(evt, cityName) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(cityName).style.display = "block";
        evt.currentTarget.className += " active";

        // Redrawing tabulator tables as they look ugly when refreshed
        if (cityName === "London") {
            tableUp.redraw();
            tableLow.redraw();

            document.getElementById("#referal-low-table2").innerHTML = "";
            document.getElementById("#referal-up-table2").innerHTML = "";

            document.getElementById("#referal-low-table3").innerHTML = "";
            document.getElementById("#referal-up-table3").innerHTML = "";

        }
        else if (cityName === "Paris") {
            tableUp2.redraw();
            tableLow2.redraw();

            document.getElementById("#referal-low-table").innerHTML = "";
            document.getElementById("#referal-up-table").innerHTML = "";

            document.getElementById("#referal-low-table3").innerHTML = "";
            document.getElementById("#referal-up-table3").innerHTML = "";
        }
        else if (cityName === "Tokyo") {
            tableUp3.redraw();
            tableLow3.redraw();

            document.getElementById("#referal-low-table").innerHTML = "";
            document.getElementById("#referal-up-table").innerHTML = "";

            document.getElementById("#referal-low-table2").innerHTML = "";
            document.getElementById("#referal-up-table2").innerHTML = "";
        }
    }

    function clickAllButs() {
        document.getElementById("sendForTable1").click();
        document.getElementById("sendForTable2").click();
        document.getElementById("sendForTable3").click();
        document.getElementById("LondonBut").click();
    }

    // For toggling visibility of graphs on demand
    function toggleDisplay(t){
        stateNow = document.getElementById(t).style.visibility;
      if (stateNow == "hidden"){
        document.getElementById(t).style.visibility = "visible";
      }
      else{
        document.getElementById(t).style.visibility = "hidden";
      }
    }

    // for loading date picker
    $(function () {
        $("#fromdatepicker").datepicker({ dateFormat: 'dd-mm-yy' });
        $("#todatepicker").datepicker({ dateFormat: 'dd-mm-yy' });
        $("#originChoices").selectmenu();
    });


    // For refreshing table on origin dropdown change
    $('#originChoices').on('selectmenuchange', function () {
        document.getElementById("sendForTable1").click();
        document.getElementById("sendForTable2").click();
        document.getElementById("sendForTable3").click();

    });
    




    // Referrals still in New Applicant stage -- Script after hitting Go
    $('#sendForTable1').on('click', function (e) {

        var eos = document.getElementById("originChoices");
        var originSelected = eos.options[eos.selectedIndex].value;



        $.ajax({
            type: "POST",
            cache: false,
            url: "/team",
            data: {
                "requestType": "InNewApplicantStage", "origin": originSelected, "fromDate": document.getElementById('fromdatepicker').value, "toDate": document.getElementById('todatepicker').value,
            }, // multiple data sent using ajax
            success: function (result) {

                // Varible for ageing avg
                let ageingAvg = 0;

                for (let i = 0; i < result.low.length; i++) {

                    // average ageing calculations
                    ageingAvg += result.low[i].Ageing;
                    if (i == result.low.length - 1) {
                        ageingAvg /= (i + 1);
                    }
                }

                document.getElementById("average-ageing-count").innerHTML = Math.round(ageingAvg);



                // Preparing data for graph of Average first action days
                var averageActionsDaysDataTable = [];
                for(r of result.side){
                    let t = [];
                    t.push(r['Recruiter Name']);
                    t.push(r['Average Action Days']);
                    averageActionsDaysDataTable.push(t);
                }

                 


                // Making graph of Average first action days
                // Load the Visualization API and the corechart package.
                  google.charts.load('current', {'packages':['corechart']});

                  // Set a callback to run when the Google Visualization API is loaded.
                  google.charts.setOnLoadCallback(drawChart);

                  // Callback that creates and populates a data table,
                  // instantiates the pie chart, passes in the data and
                  // draws it.
                  function drawChart() {

                    // Create the data table.
                    var data = new google.visualization.DataTable();
                    data.addColumn('string', 'Topping');
                    data.addColumn('number', 'Slices');
                    data.addRows(averageActionsDaysDataTable);

                    // Set chart options
                    var options = {'title':'Average Days for First Action',
                                    chartArea: {
                                      height: "80%",
                                    },
                                   'width':600,
                                   'height':600,
                                   'hAxis': {
                                    maxAlternation: 3,
                                   },
                                    legend: { position: "none" },
                                   };

                    // Instantiate and draw our chart, passing in some options.
                    var chart = new google.visualization.BarChart(document.getElementById('referal-side-graph'));
                    chart.draw(data, options);
                  }

                var whoAreTheseCandidates3 = (cell, formatterParams) => {
                    var data = cell.getData();
                    if (cell.getValue() === undefined) {
                        return
                    } else {
                        return "<a style='text-decoration:none; color:inherit;' target='_blank' href='https://tatreports.directi.com/elaborateTeamReportsNewApplicants?" + "origin=referred" + "&postingOwnerName=" + data['Recruiter Name'] + "&requestType=average" + "&fromDate=" + document.getElementById("fromdatepicker").value + "&toDate=" + document.getElementById("todatepicker").value + "'>" + cell.getValue() + "</a>";
                    }
                }

                // Table for the seeing average time take by recruiter for first action
                tableSide = new Tabulator("#referal-side-table", {
                    data: result.side,
                    layout: "fitColumns",
                    placeholder: "No Data",
                    variableHeight: true,
                    columns: [
                        { title: "Recruiter Name", field: "Recruiter Name", responsive: 0 },
                        { 
                            title: "Average Days for First Action", 
                            field: "Average Action Days",
                            formatter: whoAreTheseCandidates3, 
                        },
                    ],

                });





                google.charts.load('current', {packages: ['corechart', 'bar']});
                google.charts.setOnLoadCallback(drawStacked2);

                function drawStacked2() {
                      var data2 = new google.visualization.DataTable();
                      data2.addColumn('string', 'Time of Day');
                      data2.addColumn('number', 'Approching Deadline');
                      data2.addColumn('number', 'Crossed Deadline');

                      data2.addRows(result.side2);

                      var options2 = {
                        title: 'Candidates Approaching Deadline',
                        colors: ['#33ac71', '#9575cd'],
                        width:500,
                        height:400,
                        isStacked: true,
                        legend: {
                          position: "bottom",
                          alingment: "center",
                        },
                        hAxis: {
                          title: 'Recruiters',
                          slantedTextAngle: 45,
                          maxAlternation: 3
                        },
                        vAxis: {
                          title: 'No. of Candidates'
                        }
                      };

                      var chart2 = new google.visualization.ColumnChart(document.getElementById('referal-side-graph00'));
                      chart2.draw(data2, options2);
                    }


                var whoAreTheseCandidates2 = (cell, formatterParams) => {
                    var data = cell.getData();
                    if (cell.getValue() === undefined) {
                        return
                    } else {
                        return "<a style='text-decoration:none; color:inherit;' target='_blank' href='https://tatreports.directi.com/elaborateTeamReportsNewApplicants?" + "origin=referred" + "&postingOwnerName=" + data['Recruiter Name'] + "&requestType=c" + "&subRequestType=" + formatterParams + "&fromDate=" + document.getElementById("fromdatepicker").value + "&toDate=" + document.getElementById("todatepicker").value + "'>" + cell.getValue() + "</a>";
                    }
                }

                // Table for the seeing number of candidates crossing c
                tableSide00 = new Tabulator("#referal-side-table00", {
                    data: result.side2_table,
                    layout: "fitColumns",
                    placeholder: "No Data",
                    columns: [
                        { title: "Recruiter Name", field: "Recruiter Name", responsive: 0 },
                        { 
                            title: "Approching deadline", 
                            field: "lte_c",
                            formatter: whoAreTheseCandidates2,
                            formatterParams: "lte_c" 
                        },
                        { 
                            title: "Crossed deadline", 
                            field: "gt_c",
                            formatter: whoAreTheseCandidates2,
                            formatterParams: "gt_c" 
                        }

                    ],

                });




                // Creating a Tabulator object for lower table
                tableUp = new Tabulator("#referal-up-table", {
                    data: result.up,
                    layout: "fitColumns",
                    placeholder: "No Data",
                    columns: [
                        { title: "Recruiter", field: "Recruiter", width: 200, responsive: 0 },
                        { title: "Jan", field: "Jan", bottomCalc: "sum" },
                        { title: "Feb", field: "Feb", bottomCalc: "sum" },
                        { title: "Mar", field: "Mar", bottomCalc: "sum" },
                        { title: "Apr", field: "Apr", bottomCalc: "sum" },
                        { title: "May", field: "May", bottomCalc: "sum" },
                        { title: "Jun", field: "Jun", bottomCalc: "sum" },
                        { title: "Jul", field: "Jul", bottomCalc: "sum" },
                        { title: "Aug", field: "Aug", bottomCalc: "sum" },
                        { title: "Sept", field: "Sept", bottomCalc: "sum" },
                        { title: "Oct", field: "Oct", bottomCalc: "sum" },
                        { title: "Nov", field: "Nov", bottomCalc: "sum" },
                        { title: "Dec", field: "Dec", bottomCalc: "sum" },
                        { title: "Grand Total", field: "Grand Total", bottomCalc: "sum" },
                    ],
                });

                // Creating a Tabulator object for lower table
                tableLow = new Tabulator("#referal-low-table", {
                    data: result.low,
                    height: "60vh",
                    layout: "fitColumns",
                    placeholder: "No Data",
                    columns: [
                        { title: "Candidate Name", field: "ProfileLink", align: "center", formatter: "link", formatterParams: { target: "_blank", label: function (cell) { return cell.getRow().getData().CandidateName } } },
                        { title: "Posting Title", field: "Posting Title" },
                        { title: "Applied", field: "Applied At (GMT)", sorter: "date", sorterParams: { format: "ddd, DD MMM YYYY hh:mm:ss" } },
                        { title: "Last Story", field: "Last Story At (GMT)", sorter: "date", sorterParams: { format: "ddd, DD MMM YYYY hh:mm:ss" } },
                        { title: "Ageing", field: "Ageing" },
                        { title: "Recruiter", field: "Posting Owner Name", width: 200, headerFilter:"input" },
                    ],
                });

            }
        });
    });








    // For Response : Application to Archive -- Script after hitting 

    $('#sendForTable2').on('click', function (e) {
        var eos2 = document.getElementById("originChoices");
        var originSelected2 = eos2.options[eos2.selectedIndex].value;
        $.ajax({
            type: "POST",
            cache: false,
            url: "/team",
            data: {
                "requestType": "applicationToArchive", "origin": originSelected2, "fromDate": document.getElementById('fromdatepicker').value, "toDate": document.getElementById('todatepicker').value,
            }, // multiple data sent using ajax
            success: function (result) {

                let leaderboradDict = new Object();
                for (let i = 0; i < result.low.length; i++) {

                    if (result.low[i]['Posting Owner Name'] in leaderboradDict) {
                        leaderboradDict[result.low[i]['Posting Owner Name']].count += 1;
                        leaderboradDict[result.low[i]['Posting Owner Name']].sum += result.low[i]['Ageing'];

                    }
                    else {
                        leaderboradDict[result.low[i]['Posting Owner Name']] = { sum: 0, count: 0 };
                        leaderboradDict[result.low[i]['Posting Owner Name']].count += 1;
                        leaderboradDict[result.low[i]['Posting Owner Name']].sum += result.low[i]['Ageing'];
                    }
                }

                // Preparing leaderboardDict for tabulator

                let leaderboradDict2 = [];
                for (lea in leaderboradDict) {
                    let tempObject = new Object();
                    tempObject.name = lea;
                    tempObject.average = Math.round(leaderboradDict[lea].sum / leaderboradDict[lea].count);

                    leaderboradDict2.push(tempObject);

                }

                let ageingAvg = 0;

                for (let i = 0; i < result.low.length; i++) {
                    ageingAvg += result.low[i].Ageing;

                    if (i == result.low.length - 1) {
                        ageingAvg /= (i + 1);
                    }
                }

                document.getElementById("average-ageing-count2").innerHTML = Math.round(ageingAvg);


                // Creating a Tabulator object for lower table
                tableUp2 = new Tabulator("#referal-up-table2", {
                    data: leaderboradDict2,
                    // height: "40vh",
                    layout: "fitColumns",
                    placeholder: "No Data",
                    columns: [
                        { title: "Recruiter Name", field: "name", responsive: 0 },
                        { title: "Average Closure Days", field: "average" },

                    ],
                });

                // Creating a Tabulator object for lower table
                tableLow2 = new Tabulator("#referal-low-table2", {
                    data: result.low,
                    height: "60vh",
                    layout: "fitColumns",
                    placeholder: "No Data",
                    columns: [
                        { title: "Candidate Name", field: "ProfileLink", align: "center", formatter: "link", formatterParams: { target: "_blank", label: function (cell) { return cell.getRow().getData().CandidateName } } },
                        { title: "Posting Title", field: "Posting Title" },
                        { title: "Applied", field: "Applied At (GMT)", sorter: "date", sorterParams: { format: "ddd, DD MMM YYYY hh:mm:ss" } },
                        { title: "Posting Archived At", field: "Posting Archived At (GMT)", sorter: "date", sorterParams: { format: "ddd, DD MMM YYYY hh:mm:ss" } },
                        { title: "Ageing", field: "Ageing" },
                        { title: "Recruiter", field: "Posting Owner Name", width: 200, headerFilter:"input" },

                    ],
                });
            }
        });
    });

    $('#sendForTable3').on('click', function (e) {
        var eos3 = document.getElementById("originChoices");
        var originSelected3 = eos3.options[eos3.selectedIndex].value;

        $.ajax({
            type: "POST",
            cache: false,
            url: "/team",
            data: {
                "requestType": "applicationToOffer", "origin": originSelected3, "fromDate": document.getElementById('fromdatepicker').value, "toDate": document.getElementById('todatepicker').value,
            }, // multiple data sent using ajax
            success: function (result) {

                let leaderboradDict = new Object();
                for (let i = 0; i < result.low.length; i++) {

                    if (result.low[i]['Posting Owner Name'] in leaderboradDict) {
                        leaderboradDict[result.low[i]['Posting Owner Name']].count += 1;
                        leaderboradDict[result.low[i]['Posting Owner Name']].sum += result.low[i]['Ageing'];

                    }
                    else {
                        leaderboradDict[result.low[i]['Posting Owner Name']] = { sum: 0, count: 0 };
                        leaderboradDict[result.low[i]['Posting Owner Name']].count += 1;
                        leaderboradDict[result.low[i]['Posting Owner Name']].sum += result.low[i]['Ageing'];
                    }
                }

                // Preparing leaderboardDict for tabulator

                let leaderboradDict2 = [];
                for (lea in leaderboradDict) {
                    let tempObject = new Object();
                    tempObject.name = lea;
                    tempObject.average = Math.round(leaderboradDict[lea].sum / leaderboradDict[lea].count);

                    leaderboradDict2.push(tempObject);

                }

                let ageingAvg = 0;

                for (let i = 0; i < result.low.length; i++) {
                    ageingAvg += result.low[i].Ageing;

                    if (i == result.low.length - 1) {
                        ageingAvg /= (i + 1);
                    }
                }

                document.getElementById("average-ageing-count3").innerHTML = Math.round(ageingAvg);
                
                // Creating a Tabulator object for lower table
                tableUp3 = new Tabulator("#referal-up-table3", {
                    data: leaderboradDict2,
                    layout: "fitColumns",
                    placeholder: "No Data",
                    columns: [
                        { title: "Recruiter Name", field: "name", responsive: 0 },
                        { title: "Average Closure Days", field: "average" },
                    ],
                });

                // Creating a Tabulator object for lower table
                tableLow3 = new Tabulator("#referal-low-table3", {
                    data: result.low,
                    height: "60vh",
                    layout: "fitColumns",
                    placeholder: "No Data",
                    columns: [
                        { title: "Candidate Name", field: "ProfileLink", align: "center", formatter: "link", formatterParams: { target: "_blank", label: function (cell) { return cell.getRow().getData().CandidateName } } },
                        { title: "Posting Title", field: "Posting Title", headerFilter:"input" },
                        { title: "Applied", field: "Applied At (GMT)", sorter: "date", sorterParams: { format: "ddd, DD MMM YYYY hh:mm:ss" } },
                        { title: "Offered", field: "Stage - Offer", sorter: "date", sorterParams: { format: "ddd, DD MMM YYYY hh:mm:ss" } },
                        { title: "Ageing", field: "Ageing" },
                        { title: "Recruiter", field: "Posting Owner Name", width: 200, headerFilter:"input" },
                    ],
                });
            }
        });
    });
