function startRacing() {
  var username = document.getElementById("ntUsername").value;
  var password = document.getElementById("ntPassword").value;
  var WPM = document.getElementById("mySpeedRange").value;
  var accuracy = document.getElementById("myAccuracyRange").value;
  var nitros = document.getElementById("ntNitros").value;
  var races = document.getElementById("ntRaces").value;
  console.log(username, password, races, WPM, accuracy, nitros);
  eel.starting(username, password, races, WPM, accuracy, nitros);
}


