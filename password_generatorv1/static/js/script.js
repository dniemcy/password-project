// Restrict input length to 256 max
document.addEventListener('DOMContentLoaded', function() {
    const lengthInput = document.getElementById('length');

    lengthInput.addEventListener('input', function() {
        var value = parseInt(this.value);
        if (isNaN(value) || value < 1) {
            this.value = 1;
        } else if (value > 256) {
            this.value = 256;
        }
    });
});

// Copy to clipboard button
function copyText(event) {
    event.preventDefault();
    var copyText = document.getElementById("generatedPassword");

    copyText.select();
    copyText.setSelectionRange(0, 99999); 

    navigator.clipboard.writeText(copyText.value);

    alert("Copied the text: " + copyText.value);
}


// Generate password upon button click
function generatePassword(event) {
    event.preventDefault(); 

    var form = document.getElementById("passwordForm");
    var formData = new FormData(form);
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.password) {
                    document.getElementById("generatedPassword").value = response.password;
                } else if (response.error) {
                    console.error(response.error); 
                }
            } else {
                console.error('Request failed with status:', xhr.status);
            }
        }
    };

    xhr.onerror = function() {
        console.error('Request failed');
    };

    xhr.open("POST", "/generate-password");
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send(new URLSearchParams(formData).toString());
}


// Link input field to slider for password length
const slider = document.getElementById('lengthslider');
const numberInput = document.getElementById('length');

function updateNumberInput() {
    numberInput.value = slider.value;
}

function updateSlider() {
    slider.value = numberInput.value;
}

slider.addEventListener('input', updateNumberInput);
numberInput.addEventListener('input', updateSlider);