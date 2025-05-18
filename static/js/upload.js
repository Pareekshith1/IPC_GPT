// $(document).ready(function() {
//     $('#submitBtn').click(function(e) {
//         e.preventDefault();
//         var formData = new FormData($('#uploadForm')[0]);
//         $.ajax({
//             url: '/upload',
//             type: 'POST',
//             data: formData,
//             contentType: false,
//             processData: false,
//             success: function(data) {
//                 $('#output').html('Recognized Text: ' + data.message);
//             },
//             error: function() {
//                 $('#output').html('Error in file processing');
//             }
//         });
//     });
// });

$(document).ready(function () {
  $("#uploadForm").submit(function (e) {
    e.preventDefault();

    $("#ocrOutput").text("");
    $("#generatedOutput").text("");
    $("#loadingAnimation").show();

    var formData = new FormData(this);

    fetch("/upload", {
      method: "POST",
      body: formData,
    })
    .then((res) => res.json())
    .then((data) => {
      $("#loadingAnimation").hide();
      $("#ocrOutput").text(data.message || "No text extracted.");
      $("#generatedOutput").html(
        "<strong>🔍 Section Matches:</strong><br>" +
        (data.generated_output || "No recommendations.")
      );
    })
    .catch((err) => {
      $("#loadingAnimation").hide();
      $("#ocrOutput").text("Error occurred while processing file.");
    });
  });
});

