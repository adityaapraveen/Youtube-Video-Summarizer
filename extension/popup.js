document.addEventListener('DOMContentLoaded', function() {
  const btnSummarise = document.getElementById("summarise");
  const btnAsk = document.getElementById("ask");
  const prompt = document.querySelector(".prompt");
  const container = document.querySelector(".container");

  btnSummarise.addEventListener("click", function() {
    btnSummarise.disabled = true;
    btnSummarise.innerHTML = "Summarising...";
    chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
      var url = tabs[0].url;
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "http://127.0.0.1:5000/summary?url=" + encodeURIComponent(url), true);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var summary = xhr.responseText;
          const output = document.getElementById("output");
          output.innerHTML = summary;
          // output.innerHTML = summary;

          // Show the output div
          document.getElementById("output").style.display = "block";
          // Show the prompt and adjust styles
          prompt.style.display = "flex";
          container.style.marginRight = "20px"; // Add margin to container
        } else {
          alert("Failed to summarize the video. Please try again later.");
        }
        btnSummarise.disabled = false;
        btnSummarise.innerHTML = "Summarise";
      }
      xhr.send();
    });
  });

  btnAsk.addEventListener("click", function() {
    const question = document.getElementById("question").value;
    if (question.trim() === "") {
      alert("Please enter a question.");
      return;
    }
    chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
      var url = tabs[0].url;
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "http://127.0.0.1:5000/qa?url=" + encodeURIComponent(url) + "&question=" + encodeURIComponent(question), true);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var answer = xhr.responseText;
          const answersDiv = document.getElementById("answers");
          answersDiv.innerHTML = "<p><strong>Question:</strong> " + question + "</p><p><strong>Answer:</strong> " + answer + "</p>";
          document.getElementById("answers").style.display = "block";

        } else {
          alert("Failed to get the answer. Please try again later.");
        }
      }
      xhr.send();
    });
  });
});
