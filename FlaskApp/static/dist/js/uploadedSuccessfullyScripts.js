  // Modify title
  document.title = "Uploaded";

  $(document).ready(function () {
    $.ajax({
      type: "POST",
      cache: false,
      url: "/triggerUpdateOfDB",
      data: {},
      success: function (result) {
        console.log(result);
        document.getElementById('centerMessage').innerHTML = '<h2>' + result + '</h2><p><a href="/">Go back home</a></p>';
      }
    });
  });
