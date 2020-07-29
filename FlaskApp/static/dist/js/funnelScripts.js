    //Ajax call to load the bigDict
    $(document).ready(function () {
        $.ajax({
            type: "GET",
            cache: true,
            url: "/getBigDict",
            data: "", //ajax parameters
            success: function (result) {
                myNestedVals = result;
            }
        });

    });


    //Code inspired from http://benalexkeen.com/auto-updating-dropdown-fields-in-javascript/
    function createOption(ddl, text, value) {
        var opt = document.createElement('option');
        opt.value = value;
        opt.text = text;
        ddl.options.add(opt);
    }

    function createOptions(optionsArray, ddl) {
        optionsArray.sort();
        for (i = 0; i < optionsArray.length; i++) {
            createOption(ddl, optionsArray[i], optionsArray[i]);
        }
    }

    function configureDDL2(ddl1, ddl2, ddl3) {
        ddl2.options.length = 0;
        ddl3.options.length = 0;
        createOption(ddl2, "All", "All");
        var ddl2keys = Object.keys(myNestedVals[ddl1.value]);
        createOptions(ddl2keys, ddl2);

    }

    function configureDDL3(ddl1, ddl2, ddl3) {
        ddl3.options.length = 0;
        createOption(ddl3, "All", "All");
        var ddl3keys = myNestedVals[ddl1.value][ddl2.value];
        createOptions(ddl3keys, ddl3);
    }



    $('#send').on('click', function (e) {
        e.preventDefault();
        var x = getFormData($('#bigForm'));

        // Clearing all funnels drawn, if any. https://stackoverflow.com/questions/3955229/remove-all-child-elements-of-a-dom-node-in-javascript
        var myNode = document.getElementById("chartdivs");
        while (myNode.firstChild) {
            myNode.removeChild(myNode.firstChild);
        }

        $.ajax({
            type: "POST",
            cache: false,
            url: "/getTable",
            data: { "companyName": document.getElementById('ddl1').value, "postingTeam": document.getElementById('ddl2').value, "postingTitle": document.getElementById('ddl3').value, "postingArchiveStatus": '', "profileArchiveStatus": document.getElementById('profileArchiveStatus').value }, //ajax parameters
            success: function (result) {

                for (let i = 0; i < result.length; i++) {
                    chartVar = "chartdiv";
                    chartVar += i.toString();
                    $("#chartdivs").append(`<div style="text-align:center; margin:auto"><b>${result[i]['Posting ID']}</b><br><div  id=${chartVar}></div></div>`);

                    let var1 = 0, var2 = 0, var3 = 0, var4 = 0, var5 = 0, var6 = 0, var7 = 0;

                    for (let j = 0; j < result[i]['_children'].length; j++) {
                        var1 += result[i]['_children'][j]["newLeadCount"];
                        var2 += result[i]['_children'][j]["reachedOutCount"];
                        var3 += result[i]['_children'][j]["newApplicantCount"];
                        var4 += result[i]['_children'][j]["recruiterScreenCount"];
                        var5 += result[i]['_children'][j]["phoneInterviewCount"];
                        var6 += result[i]['_children'][j]["onsiteInterviewCount"];
                        var7 += result[i]['_children'][j]["offerCount"];
                    }

                    trigger(chartVar, var1, var2, var3, var4, var5, var6, var7);
                }


            }
        });





        function getFormData($form) {
            var unindexed_array = $form.serializeArray();
            var indexed_array = {};

            $.map(unindexed_array, function (n, i) {
                indexed_array[n['name']] = n['value'];
            });

            return indexed_array;
        }
    });
