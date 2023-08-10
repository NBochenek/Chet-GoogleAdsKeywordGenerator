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