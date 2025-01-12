$(document).ready(function() {        

    // Handle file upload form submission
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
                    fetchFeatureOverview(); // Optionally fetch the overview immediately after upload
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    // Handle reset button click
    $('#resetButton').on('click', function() {
        $.ajax({
            url: '/reset',
            type: 'POST',
            success: function(data) {
                $('#uploadForm')[0].reset();
                $('#uploadMessage').text('').removeClass('error message');
                $('#heatmap_overview').find('pre').empty();
                $('#heatmap').addClass('hidden').attr('src', '');
                $('#overviewMessage').empty();
                $('#customizeHeatmapForm')[0].reset();
                $('#customizeMessage').empty();
                $('#processForm')[0].reset();
                $('#selectedData').addClass('hidden');
                $('#selectedDataTable').empty();
                $('#heatmapResult').addClass('hidden');
                $('#selectedHeatmap').attr('src', '');
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

    // Handle "Overview Your Data" button click
    $('#overviewButton').on('click', function() {
        fetchFeatureOverview(); // Fetch and display the overview data
        $('#heatmap_overview').removeClass('hidden'); // Unhide the overview section
    });

    // Fetch and display the feature overview (data types and heatmap)
    function fetchFeatureOverview() {
        $.ajax({
            url: '/Feature_overview',
            type: 'GET',
            success: function(response) {
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    $('#data_types').text(JSON.stringify(response.data_types, null, 2));
                    $('#heatmap').attr('src', 'static/' + response.heatmap_path).removeClass('hidden');
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    }

    // Handle heatmap customization form submission
    $('#customizeHeatmapForm').on('submit', function(e) {
        e.preventDefault();
        var heatmapColors = [$('#color1').val(), $('#color2').val(), $('#color3').val()];
        var formData = {
            color1: heatmapColors[0],
            color2: heatmapColors[1],
            color3: heatmapColors[2]
        };
        $.ajax({
            url: '/customize_heatmap',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    $('#heatmap').attr('src', 'static/' + response.heatmap_path).removeClass('hidden');
                    displayMessageBox('Heatmap updated successfully.', 'message');
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    // Handle feature selection form submission
    $('#processForm').on('submit', function(e) {
        e.preventDefault();
        const form = e.target;
        const choice = form.choice.value;
        const excludeColumns = $('#excludeColumns').val();
        const numFeatures = $('#numFeatures').val();
        const target = $('#targetInput').val();
        const estimator = $('#estimator').val();
        $.ajax({
            url: '/select_features',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                choice: choice,
                excludeColumns: excludeColumns,
                numFeatures: numFeatures,
                target: target,
                estimator: estimator
            }),
            success: function(response) {
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    $('#selectedData').removeClass('hidden');
                    renderTable('#selectedDataTable', response.data);
                    $('#heatmapResult').removeClass('hidden');
                    fetchSelectedHeatmap(response.columns, heatmapColors);
                    $('#saveData').removeClass('hidden');  // Ensure the save options appear
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    // Render a table with selected features
    function renderTable(selector, data) {
        const table = $(selector);
        table.empty();

        const columns = Object.keys(data);
        const numRows = data[columns[0]].length;

        const headerRow = $('<tr>');
        columns.forEach(col => {
            headerRow.append($('<th>').text(col));
        });
        table.append(headerRow);

        for (let i = 0; i < numRows; i++) {
            const row = $('<tr>');
            columns.forEach(col => {
                row.append($('<td>').text(data[col][i]));
            });
            table.append(row);
        }
    }

    // Fetch and display the selected features heatmap
    function fetchSelectedHeatmap(columns, colors) {
        console.log("Selected columns:", columns);
        console.log("Selected colors:", colors);
    
        $.ajax({
            url: '/selected_heatmap',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({columns: columns, colors: colors}),
            success: function(response) {
                console.log("Heatmap response:", response);
                if (response.heatmap_path) {
                    $('#selectedHeatmap').attr('src', 'static/' + response.heatmap_path).removeClass('hidden');
                    $('#saveData').removeClass('hidden');  // Ensure the save options appear
                } else {
                    displayMessageBox('No heatmap path returned from server.', 'error');
                }
            },
            error: function(xhr, status, error) {
                console.log("Heatmap error:", xhr.responseText);
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    }
    

    // Handle save decision form submission
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
    
        console.log("Save form data:", formData);
    
        $.ajax({
            url: '/save',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                console.log("Save response:", response);
                displayMessageBox(response.message, 'message');
            },
            error: function(xhr) {
                console.log("Save error:", xhr.responseText);
                displayMessageBox(xhr.responseJSON.error, 'error');
            }
        });
    });

    // Function to display messages in a message box
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
