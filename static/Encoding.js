
$(document).ready(function () {
    let manualMappings = {};

    $('#uploadForm').submit(function(event) {
        event.preventDefault();
        var formData = new FormData(this);
    
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                displayMessageBox(response.message, 'message');
                uploadedFilePath = response.file_path;
                $('#overview-section').removeClass('hidden');
                fetchEncodingOverview()
                if (response.data_types) {
                    renderOverviewTable('#data_types_table', response.data_types, 'Column Name', 'Data Type');
                
            }
                if (response.column_categories) {
                    renderOverviewTable('#column_categories_table', response.column_categories, 'Column Name', 'Category');
                }
                if (response.sample_data) {
                    $('#data_simple').html(response.sample_data);
                }
            },
            error: function(response) {
                displayMessageBox(response.responseJSON?.error || "Unknown error", 'error');
            }
        });
    });
    
    let toggleDataOverviewBtn = document.getElementById('toggleDataOverview');
    if (toggleDataOverviewBtn) {
        toggleDataOverviewBtn.addEventListener('click', function () {
            var dataOverviewSection = document.getElementById('overview-section');
            if (dataOverviewSection.classList.contains('hidden')) {
                dataOverviewSection.classList.remove('hidden');
                this.textContent = 'Hide Data Overview';
            } else {
                dataOverviewSection.classList.add('hidden');
                this.textContent = 'Show Data Overview';
            }
        });
    }
    $('#resetButton').on('click', function() {
        $.ajax({
            url: '/reset',
            type: 'POST',
            success: function() {
        $('#uploadForm, #encodingForm')[0].reset();
        $('#fileInput').val(''); // This line clears the file input
        $('#filePlaceholder').text('Choose a File'); // Reset the placeholder text
        clearElements(['#uploadMessage', '#processMessage', '#saveMessage']);
        emptyElements(['#data_types_table', '#column_categories_table', '#encodingSampleDataAfter', '#pairplot']);
        toggleSections(['#saveData', '#saveOptions', '#tablebref', '#correctionForm'], false);
        manualMappings = {};
        displayMessageBox('Form reset successfully.', 'message');
    },
    error: function(xhr, status, error) {
        $('#uploadMessage').html(`<div class="alert alert-danger">An error occurred: ${xhr.responseText}</div>`);
    }
    });
    });
    document.getElementById("fileInput").addEventListener("change", function () {
        var fileName = this.files.length > 0 ? this.files[0].name : "Choose a File";
        document.getElementById("filePlaceholder").textContent = fileName;
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
    
    function handleAjaxError(xhr) {
        displayMessageBox(xhr.responseJSON?.error || 'An error occurred.', 'error');
    }

    function toggleSections(selectors, show) {
        selectors.forEach(selector => $(selector).toggleClass('hidden', !show));
    }

    function clearElements(selectors) {
        selectors.forEach(selector => $(selector).text(''));
    }

    function emptyElements(selectors) {
        selectors.forEach(selector => $(selector).empty());
    }

    $('#saveDecisionForm').on('submit', function (e) {
        e.preventDefault();
        const decision = $('input[name="save_decision"]:checked').val();
        if (decision === 'yes') {
            toggleSections(['#saveOptions'], true);
        } else if (decision === 'no') {
            $('#saveMessage').text('Data not saved.');
        } else if (decision === 'process_more') {
            toggleSections(['#saveData', '#processAnotherColumn'], [false, true]);
        }
    });

    $('#saveLocation').on('change', function () {
        toggleSections(['#customPathField'], $(this).val() === 'custom');
    });

    $('#saveFormatForm').on('submit', function (e) {
        e.preventDefault();
        const fileFormat = $('input[name="file_format"]:checked').val(),
            saveLocation = $('#saveLocation').val(),
            filename = $('#filename').val(),
            savePath = saveLocation === 'custom' ? $('#customPath').val() : saveLocation;
        
        if (!filename) return displayMessageBox('Please enter a filename.', 'error');
        if (saveLocation === 'custom' && !savePath) return displayMessageBox('Please provide a valid custom path.', 'error');
        
        $.ajax({
            url: '/save',
            type: 'POST',
            data: JSON.stringify({ file_format: fileFormat, save_path: savePath, filename: filename }),
            contentType: 'application/json',
            success: function (response) {
                displayMessageBox(response.message, 'message');
            },
            error: handleAjaxError
        });
    });

    function fetchEncodingOverview() {
        console.log('Fetching encoding overview...'); // Debugging line
        $.ajax({
            url: '/encoding_overview',
            type: 'GET',
            success: function (response) {
                console.log('Encoding overview response:', response); // Debugging line
                renderOverviewTable('#data_types_table', response.data_types, 'Column Name', 'Data Type');
                renderOverviewTable('#column_categories_table', response.column_categories, 'Column Name', 'Categories');
                $('#data_simple').html(response.sample_data);
            },
            error: handleAjaxError
        });
    }

    function renderOverviewTable(selector, data, col1Header, col2Header) {
        console.log(`Updating table: ${selector}`, data); // Debugging line
        
        const table = document.querySelector(selector);
        if (!table) {
            console.error(`Table with selector '${selector}' not found.`);
            return;
        }
        
        table.innerHTML = ''; // Clear existing content
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `<th>${col1Header}</th><th>${col2Header}</th>`;
        table.appendChild(headerRow);
        Object.entries(data).forEach(([key, value]) => {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${key}</td><td>${value}</td>`;
            table.appendChild(row);
        });
    }




    const manualEncodingInputSection = $('#manualEncodingInputSection');
    const oldValuesInput = $('#oldValuesInput');
    const newValuesInput = $('#newValuesInput');
    const manualEncodingInputs = $('#manualEncodingInputs');

    // Show/hide manual encoding input section based on encoding choice
    $('input[name="encoding_choice"]').on('change', function () {
        const isManualEncodingSelected = $('#manualEncoding').is(':checked');
        manualEncodingInputSection.toggleClass('hidden', !isManualEncodingSelected);
    });

    // Handle form submission
    $('#encodingForm').on('submit', function (e) {
        e.preventDefault();
        const encodingChoice = $('input[name="encoding_choice"]:checked').val();
        const encodingColumns = $('input[name="encoding_columns"]').val().trim();

        if (encodingChoice === 'manual') {
            // Parse old and new values
            const oldValues = oldValuesInput.val().trim();
            const newValues = newValuesInput.val().trim();

            if (!oldValues || !newValues) {
                alert('Please enter both old and new values.');
                return;
            }

            const oldValuesArray = oldValues.split(',').map(s => s.trim());
            const newValuesArray = newValues.split(',').map(s => s.trim());

            if (oldValuesArray.length !== newValuesArray.length) {
                alert('Number of old values and new values must match.');
                return;
            }

            // Store mappings in the manualMappings object
            encodingColumns.split(',').forEach(col => {
                col = col.trim();
                if (!manualMappings[col]) manualMappings[col] = {};
                oldValuesArray.forEach((oldValue, index) => {
                    manualMappings[col][oldValue] = newValuesArray[index];
                });
            });

            // Display mappings in the UI
            manualEncodingInputs.empty();
            Object.entries(manualMappings).forEach(([col, mappings]) => {
                const mappingsList = Object.entries(mappings).map(([key, value]) => `${key} -> ${value}`).join(', ');
                manualEncodingInputs.append(`<div>Column: ${col}, Mappings: ${mappingsList}</div>`);
            });
        }

        // Call the standalone processManualEncoding function
        processManualEncoding(encodingChoice, encodingColumns, manualMappings);
    });


    function processManualEncoding(encodingChoice, encodingColumns, manualMappings) {
        console.log('Processing manual encoding...'); // Debugging line
        console.log('Encoding Choice:', encodingChoice); // Debugging line
        console.log('Encoding Columns:', encodingColumns); // Debugging line
        console.log('Manual Mappings:', manualMappings); // Debugging line

        $.ajax({
            url: '/encode',
            type: 'POST',
            data: JSON.stringify({
                encoding_choice: encodingChoice,
                encoding_columns: encodingColumns,
                manual_mappings: manualMappings
            }),
            contentType: 'application/json',
            success: function (data) {
                displayMessageBox(data.message, 'message');
                $('#saveOptions').removeClass('hidden');
                $('#encodingSampleDataAfter').html(data.sample_data_after || '');
                if (data.encoding_choice === 'manual') {
                    manualMappings = {}; // Clear manual mappings
                    $('#manualEncodingInputs').empty(); // Clear the UI
                }
            },
            error: function (xhr, status, error) {
                console.error('AJAX Error:', xhr.responseText); // Debugging line
                handleAjaxError(xhr);
            }
        });
    }
    });
