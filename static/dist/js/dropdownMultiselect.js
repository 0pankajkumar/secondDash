$("#checkbox").click(function() {
  if ($("#checkbox").is(":checked")) {
    $("#e1 > option").prop("selected", "selected");
    $("#e1").trigger("change");
  } else {
    $("#e1 > option").removeAttr("selected");
    $("#e1").trigger("change");
  }
});
