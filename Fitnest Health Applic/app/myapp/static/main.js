// Set variables
var minuteTimer = 25;
var secondTimer = "00";

// Starting template for the timer
function timerTemplate() {
  document.getElementById("minutes").innerHTML = minuteTimer;
  document.getElementById("seconds").innerHTML = secondTimer;
}

function timerStart() {
  // Start the time with 5 mins
  minuteTimer = 24;
  secondTimer = 59;

  // Add minute & second to the page
  document.getElementById("minutes").innerHTML = minuteTimer;
  document.getElementById("seconds").innerHTML = secondTimer;

  // Start the countdown
  var minutesInterval = setInterval(minutesTimer, 60000);
  var secondsInterval = setInterval(secondsTimer, 1000);

  // Minute counter function
  function minutesTimer() {
    minuteTimer -= 1;
    document.getElementById("minutes").innerHTML = minuteTimer;
  }

  // Second counter function
  function secondsTimer() {
    secondTimer -= 1;
    document.getElementById("seconds").innerHTML = secondTimer;

    // Check if the seconds and minutes counter has reached 0
    // End the session when reach 0
    if (secondTimer <= 0) {
      if (minuteTimer <= 0) {
        // Clears the interval stops the counter
        clearInterval(minutesInterval);
        clearInterval(secondsInterval);
        // Alert message
        document.getElementById("done").innerHTML =
          " Time Up!! Take a Break";
        // Display message
        document.getElementById("done").classList.add("show_message");
      }
      // Reset the session
      secondTimer = 60;
    }
  }
}
