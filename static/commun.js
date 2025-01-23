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
                    uploadedFilePath = data.file_path; // Save the uploaded file path
                    displayMessageBox(data.message, 'message');
                    fetchDataOverview(); // Fetch data overview and plot after upload
                    $('#saveOptions').removeClass('hidden'); // Show save options
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });


    // Reset button handler
    $('#resetButton').on('click', function() {
        $('#uploadForm')[0].reset();
        $('#uploadMessage').text('').removeClass('error message');
        $('#dataOverview').find('pre, div').text('');
        $('#missingValuesPlot').addClass('hidden').attr('src', '');
        $('#saveOptions').addClass(''); // Hide save options
        $('#saveMessage').empty();
        uploadedFilePath = ''; // Clear the uploaded file path
        displayMessageBox('Form reset successfully.', 'message');
    });
    
    function displayMessageBox(message, type) {
        const messageBox = document.getElementById('messageBox');
        const messageContent = document.getElementById('messageContent');
        const messageButton = document.getElementById('messageButton');
    
        messageContent.textContent = message;
        
        if (type === 'error') {
            messageBox.style.backgroundColor = '#dc3545'; // Red for error
        } else if (type === 'message') {
            messageBox.style.backgroundColor = '#003fc7'; // Blue for message
        }
    
        messageBox.classList.remove('hidden');
        
        messageButton.addEventListener('click', () => {
            messageBox.classList.add('hidden');
        });
    
        setTimeout(() => {
            messageBox.classList.add('hidden');
        }, 3000); // Hide after 3 seconds
    }

    $('#saveFormatForm').on('submit', function(e) {
        e.preventDefault();
        var formData = {
            file_format: $('input[name="file_format"]:checked').val(),
            save_path: $('input[name="save_path"]').val(),
            filename: $('input[name="filename"]').val()
        };
        $.ajax({
            url: '/save',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                displayMessageBox(response.message, 'message');
            },
            error: function(response) {
                displayMessageBox(response.responseJSON.error, 'error');
            }
        });
    });
});