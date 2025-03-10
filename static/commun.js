$(document).ready(function() {
    let uploadedFilePath = ''; // Global variable to store uploaded file path

    // Handle file upload
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(data) {
                if (data.error) {
                    displayMessageBox(data.error, 'error');
                } else {
                    uploadedFilePath = data.file_path; 
                    displayMessageBox(data.message, 'message');
                    fetchDataOverview(); 
                    $('#saveOptions').removeClass('hidden'); 
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    document.getElementById("fileInput").addEventListener("change", function () {
        var fileName = this.files.length > 0 ? this.files[0].name : "Choose a File";
        document.getElementById("filePlaceholder").textContent = fileName;
    });
    // Reset button handler
    $('#resetButton').on('click', function() {
        $.ajax({
            url: '/reset',
            type: 'POST',
            success: function() {
        $('#uploadForm')[0].reset();
        $('#fileInput').val(''); // This line clears the file input
        $('#filePlaceholder').text('Choose a File'); // Reset the placeholder text
        $('#uploadMessage').text('').removeClass('error message');
        $('#dataOverview').find('pre, div').text('');
        $('#missingValuesPlot').addClass('hidden').attr('src', '');
        $('#saveOptions').addClass(''); // Hide save options
        $('#saveMessage').empty();
        uploadedFilePath = ''; // Clear the uploaded file path
        displayMessageBox('Form reset successfully.', 'message');
    },
    error: function(xhr, status, error) {
        $('#uploadMessage').html(`<div class="alert alert-danger">An error occurred: ${xhr.responseText}</div>`);
    }
});
});

function displayMessageBox(message, type) {
    const messageBox = document.getElementById('messageBox');
    const messageContent = document.getElementById('messageContent');
    const messageButton = document.getElementById('messageButton');

    messageContent.textContent = message;

    if (type === 'error') {
        messageBox.style.backgroundColor = '#dc3545'; // Red for error
    } else if (type === 'message') {
        messageBox.style.backgroundColor = ' #28a745'
    }

    messageBox.classList.remove('hidden');

    messageButton.removeEventListener('click', hideMessageBox);
    messageButton.addEventListener('click', hideMessageBox);

    setTimeout(hideMessageBox, 3000); // Hide after 3 seconds
}

function hideMessageBox() {
    document.getElementById('messageBox').classList.add('hidden');
}    

});