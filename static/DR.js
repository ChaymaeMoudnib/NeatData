$(document).ready(function() {
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
                    displayMessageBox(data.message, 'message');
                    fetchDimensionOverview();
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    $('#resetButton').on('click', function() {
        $.ajax({
            url: '/reset',
            type: 'POST',
            success: function(data) {
                $('#uploadForm')[0].reset();
                $('#uploadMessage').text('');
                $('#dimension_overview').find('pre').empty();
                $('#pairplot').addClass('hidden').attr('src', '');
                $('#overviewMessage').empty();
                $('#customizePairplotForm')[0].reset();
                $('#customizeMessage').empty();
                $('#processForm')[0].reset();
                $('#reducedData').addClass('hidden');
                $('#reducedDataContent').empty();
                $('#saveData').addClass('hidden');
                $('#saveOptions').addClass('hidden');
                $('#saveMessage').empty();
                displayMessageBox('Form reset successfully.', 'message');
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    function fetchDimensionOverview() {
        $.ajax({
            url: '/dimension_overview',
            type: 'GET',
            success: function(response) {
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    $('#data_types').text(JSON.stringify(response.data_types, null, 2));
                    $('#pairplot').attr('src', 'static/' + response.pairplot_path).removeClass('hidden');
                    $('#dimension_overview').data('data', response.data);  // Save the data for later use
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    }

    $('#customizePairplotForm').on('submit', function(e) {
        e.preventDefault();
        var formData = {
            plotColor: $('#plotColor').val(),
            plotWidth: $('#plotWidth').val(),
            plotHeight: $('#plotHeight').val()
        };
        $.ajax({
            url: '/customize_pairplot',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    $('#pairplot').attr('src', 'static/' + response.pairplot_path + '?timestamp=' + new Date().getTime()).removeClass('hidden');
                    displayMessageBox('Plot updated successfully.', 'message');
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    $('#processForm').on('submit', function(e) {
        e.preventDefault();
        const form = e.target;
        const choice = form.choice.value;
        const data = $('#dimension_overview').data('data');
        $.ajax({
            url: '/dimension',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                choice: choice,
                data: data
            }),
            success: function(response) {
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    $('#reducedData').removeClass('hidden');
                    $('#reducedDataContent').text(JSON.stringify(response, null, 2));
                    $('#saveData').removeClass('hidden');
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    $('#saveDecisionForm').on('submit', function(e) {
        e.preventDefault();
        var decision = $('input[name="save_decision"]:checked').val();
        if (decision === 'yes') {
            $('#saveOptions').removeClass('hidden');
        } else {
            $('#saveOptions').addClass('hidden');
            displayMessageBox('Data not saved.', 'message');
        }
    });

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

    function displayMessageBox(message, type) {
        const messageBox = document.getElementById('messageBox');
        const messageContent = document.getElementById('messageContent');
        const messageButton = document.getElementById('messageButton');
    
        messageContent.textContent = message;
        
        if (type === 'error') {
            messageBox.style.backgroundColor = '#dc3545'; // Red for error
        } else if (type === 'message') {
            messageBox.style.backgroundColor = '#007bff'; // Blue for message
        }
    
        messageBox.classList.remove('hidden');
        
        messageButton.addEventListener('click', () => {
            messageBox.classList.add('hidden');
        });
    
        setTimeout(() => {
            messageBox.classList.add('hidden');
        }, 3000); // Hide after 3 seconds
    }
});