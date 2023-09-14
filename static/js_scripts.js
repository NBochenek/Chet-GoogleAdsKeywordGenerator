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




