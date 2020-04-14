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