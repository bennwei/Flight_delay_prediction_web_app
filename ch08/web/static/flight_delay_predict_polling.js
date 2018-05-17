// Attach a submit handler to the form
$( "#flight_delay_classification" ).submit(function( event ) {

  // Stop form from submitting normally
  event.preventDefault();

  // Get some values from elements on the page:
  var $form = $( this ),
    term = $form.find( "input[name='s']" ).val(),
    url = $form.attr( "action" );

  // Send the data using post
  var posting = $.post(
    url,
    $( "#flight_delay_classification" ).serialize()
  );

  // Submit the form and parse the response
  posting.done(function( data ) {
    response = JSON.parse(data);

    // If the response is ok, print a message to wait and start polling
    if(response.status == "OK") {
      $( "#result" ).empty().append( "Processing..." );

      // Every 1 second, poll the response url until we get a response
      poll(response.id);
    }
  });
});

// Poll the prediction URL
function poll(id) {
  var responseUrlBase = "/flights/delays/predict/classify_realtime/response/";
  console.log("Polling for request id " + id + "...");

  // Append the uuid to the URL as a slug argument
  var predictionUrl = responseUrlBase + id;

  $.ajax(
  {
    url: predictionUrl,
    type: "GET",
    complete: conditionalPoll
  });
}

// Decide whether to poll based on the response status
function conditionalPoll(data) {
  var response = JSON.parse(data.responseText);

  if(response.status == "OK") {
    renderPage(response.prediction);
  }
  else if(response.status == "WAIT") {
    setTimeout(function() {poll(response.id)}, 1000);
  }
}

// Render the response on the page for splits:
// [-float("inf"), -15.0, 0, 30.0, float("inf")]
function renderPage(response) {

  var displayMessage;

  if(response.Prediction == 0) {
    displayMessage = "Early (15+ Minutes Early)";
  }
  else if(response.Prediction == 1) {
    displayMessage = "Slightly Early (0-15 Minute Early)";
  }
  else if(response.Prediction == 2) {
    displayMessage = "Slightly Late (0-30 Minute Delay)";
  }
  else if(response.Prediction == 3) {
    displayMessage = "Very Late (30+ Minutes Late)";
  }

  $( "#result" ).empty().append( displayMessage );
}
