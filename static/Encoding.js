let manualMappings = {};

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
                    $('#encoding_overview').removeClass('hidden'); // Show encoding overview
                    fetchEncodingOverview(); // Fetch encoding overview data
                    $('#saveOptions').removeClass('hidden'); // Show save options
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    // Handle form reset
    $('#resetButton').on('click', function() {
        $('#uploadForm')[0].reset();
        $('#encodingForm')[0].reset();
        $('#uploadMessage').text('');
        
        // Clear and hide tables
        $('#data_types_table').empty(); // Reset the data types table
        $('#column_categories_table').empty(); // Reset the column categories table
        
        $('#encodingSampleDataAfter').empty();
        $('#manualEncodingInputs').empty();
        $('#processMessage').empty();
        $('#saveData').addClass('hidden');
        $('#saveOptions').addClass('hidden');
        $('#saveMessage').empty();
        
        manualMappings = {};
        displayMessageBox('Form reset successfully.', 'message');
    });

    // Enable/disable manual mapping inputs
    $('input[name="encoding_choice"]').on('change', function() {
        if ($('#manualEncoding').is(':checked')) {
            $('#addManualMapping').prop('disabled', false);
            $('#manualEncodingInputs').show();
        } else {
            $('#addManualMapping').prop('disabled', true);
            $('#manualEncodingInputs').hide();
        }
    });

    // Handle manual mapping addition
    $('#addManualMapping').on('click', function() {
        const column = $('input[name="encoding_columns"]').val().trim();
        if (!manualMappings[column]) {
            manualMappings[column] = {};
        }
        const key = prompt('Enter the original value:');
        const value = prompt('Enter the new value:');
        if (key && value) {
            manualMappings[column][key] = value;
            const div = $('<div>').text(`Column: ${column}, ${key} -> ${value}`);
            $('#manualEncodingInputs').append(div);
        }
    });

    // Handle encoding form submission
    $('#encodingForm').on('submit', function(e) {
        e.preventDefault();
        processManualEncoding();
    });

    function processManualEncoding() {
        var formData = {
            encoding_choice: $('input[name="encoding_choice"]:checked').val(),
            encoding_columns: $('input[name="encoding_columns"]').val(),
            manual_mappings: manualMappings
        };
        $.ajax({
            url: '/encode',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(data) {
                $('#processMessage').html('<p class="message">' + data.message + '</p>');
                if (data.sample_data_after) {
                    $('#encodingSampleDataAfter').html(data.sample_data_after);
                }
                if (formData.encoding_choice === 'manual') {
                    manualMappings = {};  // Clear manual mappings after processing
                    $('#manualEncodingInputs').empty(); // Clear the displayed mappings
                }
                // Show options to process another column or save results
                $('#saveData').removeClass('hidden');
            },
            error: function(response) {
                $('#processMessage').html('<p class="error">' + response.responseJSON.error + '</p>');
            }
        });
    }

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

    

    // Handle save decision form submission
    $('#saveDecisionForm').on('submit', function(e) {
        e.preventDefault();
        var decision = $('input[name="save_decision"]:checked').val();
        if (decision === 'yes') {
            $('#saveOptions').removeClass('hidden');
        } else if (decision === 'no') {
            $('#saveMessage').text('Data not saved.');
        } else if (decision === 'process_more') {
            $('#saveData').addClass('hidden');
            $('#processAnotherColumn').show();
        }
    });

    // Handle save options form submission
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
                $('#saveMessage').html('<p class="message">' + response.message + '</p>');
            },
            error: function(response) {
                $('#saveMessage').html('<p class="error">' + response.responseJSON.error + '</p>');
            }
        });
    });

    // Handle process another column
    $('#processAnotherColumn').on('click', function() {
        $('#encodingForm')[0].reset();
        $('#manualEncodingInputs').empty();
        $('#processAnotherColumn').hide();
        $('#saveResults').hide();
        manualMappings = {};
    });

    function fetchEncodingOverview() {
        $.ajax({
            url: '/encoding_overview',
            type: 'GET',
            success: function(response) {
                renderOverviewTable('#data_types_table', response.data_types, 'Column Name', 'Data Type');
                renderOverviewTable('#column_categories_table', response.column_categories, 'Column Name', 'Categories');
            },
            error: function(xhr, status, error) {
                $('#encoding_overview').html('<p class="error">' + xhr.responseText + '</p>');
            }
        });
    }

    function renderOverviewTable(selector, data, col1Header, col2Header) {
        const table = $(selector);
        table.empty();

        const headerRow = $('<tr>');
        headerRow.append($('<th>').text(col1Header));
        headerRow.append($('<th>').text(col2Header));
        table.append(headerRow);

        Object.keys(data).forEach(key => {
            const row = $('<tr>');
            row.append($('<td>').text(key));
            row.append($('<td>').text(data[key]));
            table.append(row);
        });
    }
});
