
// Add event listner for saving the filter option
  document.getElementById("saveFilter").addEventListener("click", () => {
    // Ask for a name for filter
    defaultFilterName = "";
    var filterNamePlease = prompt("Name this filter", defaultFilterName);
    defaultFilterName = filterNamePlease;

    // Check if the name is not a duplicate
    $.ajax({
      type: "POST",
      cache: false,
      url: "/customFilters",
      data: {
        filterName: filterNamePlease,
        requestType: "checkDuplicate",
      },
      success: function(result) {
        if (result == "unique"){
        	// save the filter
        	// Send all filter options to backend
		    $.ajax({
		      type: "POST",
		      cache: false,
		      url: "/customFilters",
		      data: {
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
        else{
        	alert("Duplicate filter name encountered.\n Try another one.");
        }
      }
    });

    // If yes prompt to give another name
    // If No go forwward too save it

    
  });