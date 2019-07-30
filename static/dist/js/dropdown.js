$(function() {
  $("#ddl1").combobox({
    select: function(event, ui) {
      configureDDL2(
        ui.item,
        document.getElementById("ddl2"),
        document.getElementById("ddl3")
      );
      refresher("#ddl2");
    }
  });
  $("#ddl2").combobox({
    select: function(event, ui) {
      configureDDL3(
        document.getElementById("ddl1"),
        ui.item,
        document.getElementById("ddl3")
      );
      refresher("#ddl3");
    }
  });
  $("#ddl3").combobox({ select: function(event, ui) {} });
  $("#age").combobox();
  $("#postingArchiveStatus").combobox();

  function refresher(theID) {
    // Refresh functions inspired from https://forum.jquery.com/topic/update-jquery-ui-combobox-with-button

    //$(theID).combobox("destroy"); //first destroy the current JQuery combobox

    $(theID + " option:selected").removeAttr("selected"); //deselect the currently selected option

    //$(theID).combobox(); //Recreating the destroyed combobox
  }
});
