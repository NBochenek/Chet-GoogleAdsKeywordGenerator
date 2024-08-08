function showLoadingSpinner() {
            document.getElementById('loading-spinner').style.display = 'flex';
        }

function hideLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

function generateCustomKeywords() {
    const keywordInput = document.getElementById("input_keyword");
    const keyword = keywordInput.value.trim();
    const keywordsTextarea = document.getElementById("custom-keywords");

    if (keyword) {
        showLoadingSpinner();


        const xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                const response = JSON.parse(this.responseText);
                keywordsTextarea.value = response.keywords.join('\n');
                hideLoadingSpinner();
            } else if (this.readyState == 4) {
                const response = JSON.parse(this.responseText);
                alert(response.error);
                hideLoadingSpinner();
            }
        };
        xhttp.open("GET", "/custom_keywords?keyword=" + encodeURIComponent(keyword), true);
        xhttp.send();
    } else {
        keywordsTextarea.value = '';
        alert("Please enter a keyword.");
    }
}

function copyToClipboard(textareaId) {
    const textarea = document.getElementById(textareaId);
    textarea.select();
    document.execCommand('copy');
    // Deselect the textarea after copying
    textarea.blur();
    window.getSelection().removeAllRanges();

    // Flash message logic
    let flashMessage = document.createElement("div");
    flashMessage.className = "flash-message";
    flashMessage.innerText = "Text copied to clipboard!";

    document.body.appendChild(flashMessage);

    // Show the message
    setTimeout(() => {
        flashMessage.classList.add("show");
    }, 10);  // Delay a bit to ensure the CSS transition works

    // Hide the message after 3 seconds
    setTimeout(() => {
        flashMessage.classList.remove("show");
        // Remove the message from the DOM after hiding it
        setTimeout(() => {
            flashMessage.remove();
        }, 300);  // This should match the duration of the CSS transition
    }, 3000);
}


function sendKeyword(keyword) {
    showLoadingSpinner();

    // If no keyword argument provided, get the value from the input field
    if (!keyword) {
        keyword = document.getElementById('input_keyword').value;
    }

    fetch('/custom_keywords?keyword=' + keyword)
        .then(response => response.text())
        .then(data => {
            document.open();
            document.write(data);
            document.close();
        })
        .catch(error => console.error('Error:', error));
}

function sendSelectedKeywords() {
    showLoadingSpinner(); // Assuming this function exists to show a loading spinner

    // Gather all checkbox elements
    var checkboxes = document.querySelectorAll('input[name="selectKeyword"]:checked');

    // Extract the value of each checked checkbox
    var selectedKeywords = Array.from(checkboxes).map(function(checkbox) {
        return checkbox.value;
    });

    // Check if no keywords have been selected
    if (selectedKeywords.length === 0) {
        hideLoadingSpinner()
        alert('No Keywords Selected. Please Try Again.');
        return; // Stop the function execution
    }

    // Use fetch to create a POST request to send the data
    fetch('/selected_keywords', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({keywords: selectedKeywords})
    })
    .then(response => response.text())
    .then(data => {
        document.open();
        document.write(data);
        document.close();
    })
    .catch(error => {
        console.error('Error:', error);
        // Optionally, stop the spinner if there's an error
    });
}



function toggleDropdown() {
    var dropdownContent = document.querySelector(".dropdown-content");
    if (dropdownContent.style.display === "block") {
        dropdownContent.style.display = "none";
    } else {
        dropdownContent.style.display = "block";
    }
}

function sendKeywordToNewTab(keyword) {
    showLoadingSpinner();
    fetch('/targeted_keywords?keyword=' + keyword)
        .then(response => response.text())
        .then(data => {
            let newWindow = window.open('', '_blank');
            newWindow.document.open();
            newWindow.document.write(data);
            newWindow.document.close();
            hideLoadingSpinner();
        })
        .catch(error => console.error('Error:', error));
}

function submitFeedback(type, event) {
    const buttons = document.querySelectorAll('.feedback-button'); // Select all buttons
    buttons.forEach(button => button.disabled = true); // Disable all buttons

    fetch('/submit_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `feedback=${encodeURIComponent(type)}`
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        alert('Thank you for your feedback!');
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('Error submitting feedback');
        buttons.forEach(button => button.disabled = false); // Optionally re-enable the buttons on error if desired
    });
}

function sortTable(column) {
  var table, rows, switching, i, x, y, shouldSwitch, direction, switchcount = 0;
  table = document.querySelector(".metric-table");
  switching = true;
  direction = "asc"; // Set the sorting direction to ascending initially

  while (switching) {
    switching = false;
    rows = table.rows;
    for (i = 1; i < (rows.length - 1); i++) { // Skip the header row
      shouldSwitch = false;
      x = rows[i].getElementsByTagName("TD")[column];
      y = rows[i + 1].getElementsByTagName("TD")[column];

      // Check if the column should be parsed as integer
      let xContent = (column === 1 || column === 2) ? parseInt(x.innerHTML, 10) : x.innerHTML.toLowerCase();
      let yContent = (column === 1 || column === 2) ? parseInt(y.innerHTML, 10) : y.innerHTML.toLowerCase();

      if (direction == "asc") {
        if (xContent > yContent) {
          shouldSwitch = true;
          break;
        }
      } else if (direction == "desc") {
        if (xContent < yContent) {
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    } else {
      if (switchcount == 0 && direction == "asc") {
        direction = "desc";
        switching = true;
      }
    }
  }
}








