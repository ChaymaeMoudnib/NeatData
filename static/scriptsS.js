document.addEventListener("DOMContentLoaded", function() {
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
                    fetchSamplingOverview();
                    $('#sampling_overview').removeClass('hidden');

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
                $('#uploadMessage').text('').removeClass('error message');
                $('#fileInput').val(''); // This line clears the file input
                $('#filePlaceholder').text('Choose a File'); // Reset the placeholder text
                    $('#data_types_table').empty();
                $('#data_info_table').empty();
                $('#samplingForm')[0].reset();
                $('#samplingMessage').empty();
                $('#sampledData').addClass('hidden');
                $('#sampledDataTable').empty();
                $('#analysisResults').addClass('hidden');
                $('#analysisResultsTable').empty();
                $('#samplingErrors').addClass('hidden');
                $('#samplingErrorsTable').empty();
                $('#visualizations').addClass('hidden');
                $('#visualizationContainer').empty();
                $('#saveOptions').addClass('hidden'); // Hide save options on reset
                $('#saveMessage').empty();
                displayMessageBox('Form reset successfully.', 'message');
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            }
        });
    });

    $(document).ready(function() {
        fetchSamplingOverview();
        
        $('#samplingForm').on('submit', function(e) {
            e.preventDefault();
            var formData = {
                samplingMethod: $('#samplingMethod').val(),
                sampleSize: $('#sampleSize').val(),
                stratifyColumn: $('#stratifyColumn').val(),
                numClusters: $('#numClusters').val() || 0,
                clusterColumn: $('#clusterColumn').val()
            };
            $.ajax({
                url: '/sample_data',
                type: 'POST',
                data: JSON.stringify(formData),
                contentType: 'application/json',
                success: function(response) {
                    if (response.error) {
                        displayMessageBox(response.error, 'error');
                    } else {
                        $('#sampledData').removeClass('hidden');
                        renderTable('#sampledDataTable', response.sampled_data);
                        $('#analysisResults').removeClass('hidden');
                        renderAnalysisResults(response.analysis_results);
                        $('#samplingErrors').removeClass('hidden');
                        renderSamplingErrors(response.errors);
                        $('#saveOptions').removeClass('hidden'); // Show save options on successful submission
                        displayMessageBox('Data sampled successfully.', 'message');
                    }
                },
                error: function(xhr, status, error) {
                    displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
                }
            });
        });

        $('#samplingMethod').on('change', function() {
            const method = $(this).val();
            $('#stratifiedOptions').toggleClass('hidden', method !== 'stratified');
            $('#clusterOptions').toggleClass('hidden', method !== 'cluster');
            $('#sampleSize').prop('required', method !== 'convenience');
        });
    });

    function fetchSamplingOverview() {
        $.ajax({
            url: '/sampling_overview',
            type: 'GET',
            success: function(response) {
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    renderOverviewTable('#data_types_table', response.data_types, 'Column', 'Type');
                    renderOverviewTable('#data_info_table', response.data_info, 'Info', 'Value');
                }
            },
            error: function(xhr, status, error) {
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
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
    
    $(document).ready(function() {
        fetchSamplingOverview();
    });

    
    function renderTable(selector, data) {
        const table = $(selector);
        table.empty();
    
        const columns = Object.keys(data);
        const numRows = Math.min(10, data[columns[0]].length); // Limit to 10 rows
        const maxCols = Math.min(5, columns.length); // Limit displayed columns
    
        const headerRow = $('<tr>');
        for (let i = 0; i < maxCols; i++) {
            headerRow.append($('<th>').text(columns[i]));
        }
        table.append(headerRow);
    
        for (let i = 0; i < numRows; i++) {
            const row = $('<tr>');
            for (let j = 0; j < maxCols; j++) {
                row.append($('<td>').text(data[columns[j]][i]));
            }
            table.append(row);
        }
    }
    
    function renderAnalysisResults(results) {
        const table = $('#analysisResultsTable');
        table.empty();
    
        const headerRow = $('<tr>');
        headerRow.append($('<th>').text('Measure'));
        Object.keys(results.mean).forEach(col => {
            headerRow.append($('<th>').text(col));
        });
        table.append(headerRow);
    
        const measures = {
            "Mean": results.mean,
            "Median": results.median,
            "Standard Deviation": results.std,
            "Variance": results.var,
            "Min": results.min,
            "Max": results.max,
            "Q1": results.quartiles.Q1,
            "Q2": results.quartiles.Q2,
            "Q3": results.quartiles.Q3
        };
    
        Object.keys(measures).forEach(measure => {
            const row = $('<tr>');
            row.append($('<td>').text(measure));
            Object.keys(results.mean).forEach(col => {
                row.append($('<td>').text(measures[measure][col]));
            });
            table.append(row);
        });
    }

    function renderSamplingErrors(errors) {
        const table = $('#samplingErrorsTable');
        table.empty();
        
        const headerRow = $('<tr>');
        headerRow.append($('<th>').text('Error Type'));
        headerRow.append($('<th>').text('Column'));
        headerRow.append($('<th>').text('Value'));
        headerRow.append($('<th>').text('Explanation'));
        table.append(headerRow);
        
        Object.keys(errors).forEach(errorType => {
            const errorValue = errors[errorType];
    
            if (errorType === 'non_response_error') {
                const row = $('<tr>');
                const explanation = 'High non-response rate indicates that a large portion of the population did not participate.';
                row.append($('<td>').text(errorType));
                row.append($('<td>').text(''));
                row.append($('<td>').text(errorValue['rate']));
                row.append($('<td>').text(explanation));
                table.append(row);
            } else if (errorType === 'sampling_error') {
                Object.keys(errorValue).forEach(subErrorType => {
                    const row = $('<tr>');
                    const subErrorValue = errorValue[subErrorType];
                    const explanation = generateSamplingErrorExplanation(subErrorValue, subErrorType);
                    
                    row.append($('<td>').text(errorType));
                    row.append($('<td>').text(subErrorType));
                    row.append($('<td>').text(subErrorValue));
                    row.append($('<td>').text(explanation));
                    table.append(row);
                });
            } else if (errorType === 'selection_error') {
                Object.keys(errorValue).forEach(columnName => {
                    const subErrorValue = errorValue[columnName];
                    Object.keys(subErrorValue).forEach(key => {
                        const row = $('<tr>');
                        const explanation = generateSelectionErrorExplanation(key, subErrorValue[key]);
    
                        row.append($('<td>').text(errorType));
                        row.append($('<td>').text(columnName));
                        row.append($('<td>').text(`${key}: ${subErrorValue[key]}`));
                        row.append($('<td>').text(explanation));
                        table.append(row);
                    });
                });
            } else {
                const row = $('<tr>');
                row.append($('<td>').text(errorType));
                row.append($('<td>').text(''));
                row.append($('<td>').text(JSON.stringify(errorValue, null, 2)));
                row.append($('<td>').text(''));
                table.append(row);
            }
        });
    }
    
    function generateSamplingErrorExplanation(value, errorType) {
        if (value > 0) {
            return `${errorType} is higher in the sample compared to the population.`;
        } else if (value < 0) {
            return `${errorType} is lower in the sample compared to the population.`;
        } else {
            return `${errorType} in the sample is equal to the population.`;
        }
    }
    
    function generateSelectionErrorExplanation(key, value) {
        if (key === 'selection_bias') {
            if (value > 0) {
                return `Sample variability is ${value}% higher than the population.`;
            } else if (value < 0) {
                return `Sample variability is ${value}% lower than the population.`;
            } else {
                return `Sample variability is equal to the population.`;
            }
        } else if (key === 'population_std') {
            return 'Standard deviation of the population.';
        } else if (key === 'sample_std') {
            return 'Standard deviation of the sample.';
        } else {
            return '';
        }
    }

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
    

let toggleDataOverviewBtn = document.getElementById('toggleSamplingOverview');
    if (toggleDataOverviewBtn) {
        toggleDataOverviewBtn.addEventListener('click', function () {
            var dataOverviewSection = document.getElementById('sampling_overview');
            if (dataOverviewSection.classList.contains('hidden')) {
                dataOverviewSection.classList.remove('hidden');
                dataOverviewSection.style.marginTop = '20px'; 
                this.textContent = 'Hide Data Overview';
            } else {
                dataOverviewSection.classList.add('hidden');
                dataOverviewSection.style.marginTop = '0';
                this.textContent = 'Show Data Overview';
            }
        });
        toggleDataOverviewBtn.style.marginBottom = '20px'; // Adjust this value as needed
    }

});
