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
            if(result.resultFound == "yes"){
                // Selecting the Company name programatically
                $('#ddl1').val(result.companyName);
                $("#ddl1").trigger("change");
                
            }
            else {
                document.getElementById("snackbar").innerHTML = "Filter not loaded\n Try selecting manually";
                triggerSnackbar();
            }
            let dict = {
                pageType: result.pageType,
                companyName: result.companyName,
                postingTeam: result.postingTeam,
                postingTitle: result.postingTitle,
                postingArchiveStatus: result.postingArchiveStatus,
                profileArchiveStatus: result.profileArchiveStatus,
                fromDate: result.fromDate,
                toDate: result.toDate,
                recruiter: result.recruiter
            };
        }
    });


}