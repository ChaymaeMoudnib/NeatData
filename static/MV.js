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
                    fetchDataOverview();
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
                $('#dataOverview').find('pre, div').text('');
                $('#missingValuesPlot').addClass('hidden').attr('src', '');
                displayMessageBox('Form reset successfully.', 'message');
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    function fetchDataOverview() {
        var missingColor = $('#missingColor').val();
        var presentColor = $('#presentColor').val();
        
        $.ajax({
            url: '/data_overview',
            type: 'GET',
            data: {
                missingColor: missingColor,
                presentColor: presentColor
            },
            success: function(response) {
                $('#missingDataTable').html(response.missing_data_table);
                $('#sampleData').html(response.sample_data);
                $('#missingValuesPlot').attr('src', 'static/' + response.missing_values_plot).removeClass('hidden');
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    }

    $('#plotCustomizationForm').on('submit', function(e) {
        e.preventDefault(); // Prevent the default form submission
        // Your AJAX code here
    
        var plotData = {
            colorMap: $('#colorMap').val(),
            plotWidth: $('#plotWidth').val(),
            plotHeight: $('#plotHeight').val(),
            missingColor: $('#missingColor').val(),
            presentColor: $('#presentColor').val()
        };
        $.ajax({
            url: '/customize_plot',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(plotData),
            success: function(response) {
                $('#missingValuesPlot').attr('src', 'static/' + response.missing_values_plot).removeClass('hidden');
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    $('input[name="choice"]').change(function() {
        if ($(this).val() === '3') {
            $('#imputationMethods').removeClass('hidden');
        } else {
            $('#imputationMethods').addClass('hidden');
            $('#knnNeighbors').addClass('hidden');
            $('#miceParams').addClass('hidden');
        }
    });

    $('input[name="impute_choice"]').change(function() {
        if ($(this).val() === '1') {
            $('#knnNeighbors').removeClass('hidden');
            $('#miceParams').addClass('hidden');
        } else if ($(this).val() === '6') {
            $('#miceParams').removeClass('hidden');
            $('#knnNeighbors').addClass('hidden');
        } else {
            $('#knnNeighbors').addClass('hidden');
            $('#miceParams').addClass('hidden');
        }
    });

    $('#processForm').on('submit', function(e) {
        e.preventDefault();
        var formData = {
            choice: $('input[name="choice"]:checked').val(),
            columns: $('input[name="columns"]').val(),
            impute_choice: $('input[name="impute_choice"]:checked').val(),
            n_neighbors: $('input[name="n_neighbors"]').val(),
            max_iter: $('input[name="max_iter"]').val()
        };
        $.ajax({
            url: '/process',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                displayMessageBox(response.message, 'message');
                $('#saveData').removeClass('hidden');
            },
            error: function(response) {
                displayMessageBox(response.responseJSON.error, 'error');
            }
        });
    });

    $('#saveDecisionForm').on('submit', function(e) {
        e.preventDefault();
        var decision = $('input[name="save_decision"]:checked').val();
        if (decision === 'yes') {
            $('#saveOptions').removeClass('hidden');
        } else if (decision === 'process_more') {
            $('#saveData').addClass('hidden');
            $('#processMessage').addClass('hidden');
            $('#dataOverview').removeClass('hidden');
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