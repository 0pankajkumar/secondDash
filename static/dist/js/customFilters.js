// Add event listner for saving the filter option
document.getElementById("saveFilter").addEventListener("click", () => {
    // Ask for a name for filter
    defaultFilterName = "";
    var filterNamePlease = prompt("Name this filter", defaultFilterName);
    defaultFilterName = filterNamePlease;

    if (filterNamePlease != null) {
        if (filterNamePlease == "") {
            document.getElementById("snackbar").innerHTML = "Anonymous filters are dangerous";
            triggerSnackbar();
        } else {
            // Send all filter options to backend
            $.ajax({
                type: "POST",
                cache: false,
                url: "/customFilters",
                data: {
                    filterName: filterNamePlease,
                    pageType: document.title,
                    companyName: document.getElementById("ddl1").value,
                    postingTeam: document.getElementById("ddl2").value,
                    postingTitle: $("#ddl3").val(),
                    postingArchiveStatus: "",
                    profileArchiveStatus: document.getElementById("profileArchiveStatus")
                        .value,
                    from: document.getElementById("fromdatepicker").value,
                    to: document.getElementById("todatepicker").value,
                    requestType: "save",
                    recruiter: "All"
                },
                success: function(result) {
                    document.getElementById("snackbar").innerHTML = result;
                    triggerSnackbar();
                }
            });
        }
    }

});





function dateIntify(fromDate, toDate) {
    let d = {};
    if (fromDate.length > 8) {

        d.fromDateYear = parseInt(fromDate.slice(0, 4));
        d.fromDateMonth = parseInt(fromDate.slice(5, 7));
        d.fromDateDay = parseInt(fromDate.slice(8, 10));
    }

    if (toDate.length > 8) {
        d.toDateYear = parseInt(toDate.slice(0, 4));
        d.toDateMonth = parseInt(toDate.slice(5, 7));
        d.toDateDay = parseInt(toDate.slice(8, 10));
    }

    return d;

}



// Apply custom filter to all the dropdowns below
function applyCustomFilterWaterfall(selectedCustomFilter) {

    // Fetch all data of selectedCustomFilter
    $.ajax({
        type: "POST",
        cache: false,
        url: "/customFilters",
        data: {
            filterName: selectedCustomFilter.value,
            requestType: "getThoseOptions"
        },
        success: function(result) {
            if (result.resultFound == "yes") {
                // Selecting the Company name programatically
                $('#ddl1').val(result.companyName);
                $("#ddl1").trigger("change");

                $('#ddl2').val(result.postingTeam);
                $("#ddl2").trigger("change");

                $('#ddl3').val(result.postingTitle);
                $("#ddl3").trigger("change");

                $('#profileArchiveStatus').val(result.profileArchiveStatus);
                $("#profileArchiveStatus").trigger("change");

                let formatDatesPlease = dateIntify(result.fromDate, result.toDate)

                if (result.fromDate.length > 8) {
                    $('#fromdatepicker').datepicker("setDate", new Date(formatDatesPlease.fromDateYear, formatDatesPlease.fromDateMonth, formatDatesPlease.fromDateDay));
                    $("#fromdatepicker").trigger("change");
                }
                if (result.toDate.length > 8) {
                    $('#todatepicker').datepicker("setDate", new Date(formatDatesPlease.toDateYear, formatDatesPlease.toDateMonth, formatDatesPlease.toDateDay));
                    $("#todatepicker").trigger("change");
                }
                document.getElementById("sendForTable").click();

            } else {
                document.getElementById("snackbar").innerHTML = "Filter not loaded\n Try selecting manually";
                triggerSnackbar();
            }
        }
    });


}










// Delete filter defined below
document.getElementById("deleteFilter").addEventListener("click", () => {
    filterName = document.getElementById("ddl0").value;
    if (filterName != null || filterName != "") {
        // Sending filterName to delete it from records
        $.ajax({
            type: "POST",
            cache: false,
            url: "/customFilters",
            data: {
                filterName: filterName,
                requestType: "delete"
            },
            success: function(result) {
                document.getElementById("snackbar").innerHTML = result;
                triggerSnackbar();
            }
        });
    }
});


// Share filter opening & closing
function openShareDialog() {
    document.getElementById("shareDialog").style.display = "block";
}

function closeShareDialog() {
    document.getElementById("shareDialog").style.display = "none";
}

document.getElementById("shareFilter").addEventListener("click", () => {
    openShareDialog();
    // Get all user names
    $.ajax({
            type: "POST",
            cache: false,
            url: "/customFilters",
            data: {
                requestType: "getAllUsernameForSharing"
            },
            success: function(result) {
                if (result.foundUsernames == "yes") {
                    // Create options & poplulate it in multiselect
                    let allUsernames = result.usernames;
                    let ddl = document.getElementById("shareSelect");
                    createOptions(allUsernames, ddl);

                    $('.shareSelect').select2();

                    // On click of send, send it to server & close
                    document.getElementById("shareFilter").addEventListener("shareTrigger", () => {
                            // Sending to server
                            $.ajax({
                                    type: "POST",
                                    cache: false,
                                    url: "/customFilters",
                                    data: {
                                        requestType: "shareToThesePeople",
                                        usernamesToBeSharedWith: $("#shareSelect").val()
                                    },
                                    success: function(result2) {
                                        // display response from server
                                        document.getElementById("snackbar").innerHTML = result2;
                                        triggerSnackbar();
                                        closeShareDialog();
                                    });
                            });
                    }
                }
            });

    });

});