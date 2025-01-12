let manualMappings = {};

        $(document).ready(function() {
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
                            $('#uploadMessage').text(data.error).addClass('error');
                        } else {
                            $('#uploadMessage').text(data.message).addClass('message');
                            fetchEncodingOverview();
                        }
                    },
                    error: function(xhr, status, error) {
                        $('#uploadMessage').text('An error occurred: ' + xhr.responseText).addClass('error');
                    }
                });
            });

            // Handle form reset
            $('#resetButton').on('click', function() {
                $('#uploadForm')[0].reset();
                $('#encodingForm')[0].reset();
                $('#uploadMessage').text('');
                $('#encoding_overview').find('pre').empty();
                $('#encodingSampleDataAfter').empty();
                $('#manualEncodingInputs').empty();
                $('#processMessage').empty();
                $('#saveData').addClass('hidden');
                $('#saveOptions').addClass('hidden');
                $('#saveMessage').empty();
                manualMappings = {};
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
                        populateTable('#data_types', response.data_types);
                        populateTable('#column_categories', response.column_categories);
                    },
                    error: function(xhr, status, error) {
                        $('#encoding_overview').html('<p class="error">' + xhr.responseText + '</p>');
                    }
                });
            }

            function populateTable(selector, data) {
                var table = $(selector);
                table.empty();
                var thead = $('<thead>');
                var tbody = $('<tbody>');
                var headers = Object.keys(data).map(function(key) {
                    return $('<th>').text(key);
                });
                thead.append($('<tr>').append(headers));
                var rows = Object.keys(data).map(function(key) {
                    return $('<td>').text(JSON.stringify(data[key]));
                });
                tbody.append($('<tr>').append(rows));
                table.append(thead).append(tbody);
            }
        });