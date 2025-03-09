$(document).ready(function () {
    const $spinner = $('#spinner');
    const $uploadForm = $('#uploadForm');
    const $resetButton = $('#resetButton');
    const $customizePairplotForm = $('#customizePairplotForm');
    const $saveDecisionForm = $('#saveDecisionForm');
    const $saveFormatForm = $('#saveFormatForm');
    const $toggleTechniques = $('#toggleTechniques');
    const $toggleDataOverview = $('#toggleDataOverview');
    const $messageBox = $('#messageBox');
    const $messageContent = $('#messageContent');
    const $messageButton = $('#messageButton');


    // Get the file input and the display element
    const fileUpload = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    
    // Add an event listener to the file input
    fileUpload.addEventListener('change', function (event) {
        if (event.target.files.length > 0) {
            const fileName = event.target.files[0].name;
            fileNameDisplay.innerHTML = `Uploaded File: <strong>${fileName}</strong>`;
        } else {
            fileNameDisplay.innerHTML = '';
        }
    });
    function showSpinner() {
        const spinner = document.querySelector('.spinner');
        const functionalitySection = document.querySelector('.functionality-section');
        if (spinner && functionalitySection) {
            const rect = functionalitySection.getBoundingClientRect();
            spinner.style.position = 'fixed';
            spinner.style.top = `${rect.top}px`;
            spinner.style.left = `${rect.left}px`;
            spinner.style.width = `${rect.width}px`;
            spinner.style.height = `${rect.height}px`;
            spinner.classList.remove('hidden');
        }
    }
    
    function hideSpinner() {
        const spinner = document.querySelector('.spinner');
        if (spinner) {
            spinner.classList.add('hidden');
        }
    }
    document.getElementById('uploadForm').addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent form submission for demonstration
        showSpinner();
    });
    document.getElementById('processForm').addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent form submission for demonstration
        showSpinner();
    });
    
    $(document)
        .on('submit', '#uploadForm', handleUpload)
        .on('click', '#resetButton', handleReset)
        .on('submit', '#customizePairplotForm', handleCustomizePairplot)
        .on('submit', '#saveOptions', handleSaveFormat)
        .on('click', '#toggleTechniques', toggleTechniques)
        .on('click', '#toggleDataOverview', toggleDataOverview)
        .on('click', '#processForm', handleprocess);
    // Handle file upload
    function handleUpload(e) {
        e.preventDefault();
        const formData = new FormData(this);
        $spinner.removeClass('hidden');

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                //$spinner.addClass('hidden');
                hideSpinner();
                if (data.error) {
                    displayMessageBox(data.error, 'error');
                } else {
                    displayMessageBox(data.message, 'message');
                    fetchDimensionOverview();
                }
            },
            error: handleAjaxError,
        });
    }

    // Handle reset button click
    function handleReset() {
        $.ajax({
            url: '/reset',
            type: 'POST',
            success: function (data) {
                $toggleDataOverview.removeClass('hidden');
                $uploadForm[0].reset();
                $('#uploadMessage').text('');
                
                // Reset file input and placeholder
                $('#fileInput').val(''); // This line clears the file input
                $('#filePlaceholder').text('Choose a File'); // Reset the placeholder text
    
                $('#dimension_overview').find('pre').empty();
                $('#pairplot, #correlation').addClass('hidden').attr('src', '');
                $('#overviewMessage, #customizeMessage, #saveMessage').empty();
                $('#customizePairplotForm, #processForm')[0].reset();
                $('#reducedData, #data_types, #saveData, #saveOptions').addClass('hidden');
                $('#reducedDataContent').empty();
                emptyElements(['#data_types', '#correlation', '#manualEncodingInputs']);
                displayMessageBox('Form reset successfully.', 'message');
            },
            error: handleAjaxError,
        });
    }
    
    /// dimension
function handleprocess(e) {
    const form = document.getElementById("processForm");
    const targetFeatureFields = document.getElementById("targetFeatureFields");
    const autoencoderFields = document.getElementById("autoencoderFields");
    const resultsDiv = document.getElementById("results");

    function toggleFields() {
        const choice = document.querySelector('input[name="choice"]:checked').value;
        
        if (choice === "1") { // PCA
            targetFeatureFields.style.display = "none";
            autoencoderFields.style.display = "none";
        } else if (choice === "2") { // RFE
            targetFeatureFields.style.display = "block";
            autoencoderFields.style.display = "none";
        } else if (choice === "3") { // AEFS
            targetFeatureFields.style.display = "block";
            autoencoderFields.style.display = "block";
        }
    }

    // Initialize fields based on default choice
    toggleFields();

    document.querySelectorAll('input[name="choice"]').forEach(input => {
        input.addEventListener("change", toggleFields);
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        //$spinner.removeClass('hidden')
        
        const choice = document.querySelector('input[name="choice"]:checked').value;
        const target = document.getElementById("target").value || null;
        const num_features = document.getElementById("num_features").value || 5;
        const hidden_layer_size = document.getElementById("hidden_layer_size").value || 10;
        const max_iter = document.getElementById("max_iter").value || 1000;
        const exclude_numeric = document.getElementById("exclude_numeric").value || "";
        const exclude_categorical = document.getElementById("exclude_categorical").value || "";

        // Validate numeric inputs
        if (isNaN(num_features) || isNaN(hidden_layer_size) || isNaN(max_iter)) {
            alert("Please enter valid numbers for numeric fields.");
            return;
        }

        const requestData = {
            choice,
            target,
            num_features: parseInt(num_features),
            hidden_layer_size: parseInt(hidden_layer_size),
            max_iter: parseInt(max_iter),
            exclude_numeric: exclude_numeric.split(",").map(col => col.trim()).filter(Boolean),
            exclude_categorical: exclude_categorical.split(",").map(col => col.trim()).filter(Boolean)
        };
        $spinner.removeClass('hidden'),
        fetch("/dimension", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            hideSpinner();
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                displayResults(choice === "1" ? "PCA" : (choice === "2" ? "RFE" : "AEFS"), data);
                $('#saveOptions').removeClass('hidden');
            }
        })
        .catch(error => {
            alert("An error occurred: " + error);
        });
    });
}

function displayResults(method, results) {
    document.getElementById("results").style.display = "none";
    document.getElementById("pcaResults").style.display = "none";
    document.getElementById("rfeResults").style.display = "none";
    
    if (method === 'PCA') {
        document.getElementById("explainedVariance").innerText = results.explained_variance || "N/A";
        document.getElementById("contributions").innerText = results.message || "No message";
        document.getElementById("pcaResults").style.display = "block";
        
        if (results.visualization_data) {
            const { components, explained_variance, cumulative_variance, optimal_components } = results.visualization_data;

            const individualTrace = {
                x: components,
                y: explained_variance,
                type: 'bar',
                name: 'Individual Explained Variance',
                marker: { color: 'lightblue' }
            };

            const cumulativeTrace = {
                x: components,
                y: cumulative_variance,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Cumulative Explained Variance',
                line: { color: 'orange', width: 2 }
            };

            const optimalLine = {
                x: [optimal_components, optimal_components],
                y: [0, 1],
                mode: 'lines',
                line: { color: 'red', dash: 'dash' },
                name: `Optimal Components (≥80%): ${optimal_components}`
            };

            const layout = {
                title: {
                    text: 'Cumulative Explained Variance by Principal Components',
                    font: { size: 14 }, // Adjust title font size
                },
                xaxis: { 
                    title: 'Principal Component',
                    titlefont: { size: 12}, // Adjust x-axis title font size
                },
                yaxis: { 
                    title: 'Explained Variance Ratio',
                    titlefont: { size: 12 }, // Adjust y-axis title font size
                },
                legend: { 
                    x: 0.02, 
                    y: 0.98,
                    font: { size: 12 }, // Adjust legend font size
                },
                showlegend: true,
                margin: { t: 40, l: 50, r: 50, b: 40 }, // Adjust margins
                height: 300, // Set a fixed height for the plot
                width: 400, // Set a fixed width for the plot
            };

            // Render the plot
            Plotly.newPlot('pcaPlot', [individualTrace, cumulativeTrace, optimalLine], layout);
        }
    } else if (method === 'RFE' || method === 'AEFS') {
        document.getElementById("selected_features").innerText = results.selected_features || "N/A";
        document.getElementById("rfeResults").style.display = "block";
    }
    
    document.getElementById("results").style.display = "block";
}

    
    // Fetch dimension overview
    function fetchDimensionOverview() {
        showSpinner();
        $toggleDataOverview.addClass('hidden');

        $.ajax({
            url: '/dimension_overview',
            type: 'GET',
            success: function (response) {
                hideSpinner();
                $toggleDataOverview.removeClass('hidden');

                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    if (response.data_types) {
                        renderDataTypesTable(response.data_types);
                    }
                    $('#correlation').attr('src', 'static/' + response.correlation).removeClass('hidden');
                    $('#pairplot').attr('src', 'static/images/' + response.pairplot_path).removeClass('hidden');
                    $('#dimension_overview').data('data', response.data);
                }
            },
            error: handleAjaxError,
        });
    }

    function renderDataTypesTable(dataTypes) {
        console.log("Rendering Table, Data:", dataTypes);
        if (!dataTypes || Object.keys(dataTypes).length === 0) {
            console.error("No data types to render!");
            return;
        }
    
        let html = '<table border="1" cellpadding="10" cellspacing="0">';
        html += '<tr><th>Column</th><th>Data Type</th></tr>';
        
        Object.entries(dataTypes).forEach(([column, dtype]) => {
            html += `<tr><td>${column}</td><td>${dtype}</td></tr>`;
        });
    
        html += '</table>';
        $('#data_types').html(html).show();
    }
    

    // Handle pairplot customization
    function handleCustomizePairplot(e) {
        $spinner.removeClass('hidden');
        e.preventDefault();
        const formData = {
            plotColor: $('#plotColor').val(),
            plotWidth: $('#plotWidth').val(),
            plotHeight: $('#plotHeight').val(),
        };

        $.ajax({
            url: '/customize_pairplot',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                $spinner.addClass('hidden');
                if (response.error) {
                    displayMessageBox(response.error, 'error');
                } else {
                    $('#pairplot').attr('src', 'static/images/' + response.pairplot_path + '?timestamp=' + new Date().getTime()).removeClass('hidden');
                    displayMessageBox('Plot updated successfully.', 'message');
                }
            },
            error: handleAjaxError,
        });
    }



    // Handle save format
    $(document).ready(function () {
        // Show/hide custom path input based on selection
        $('#saveLocation').on('change', function () {
            if ($(this).val() === 'custom') {
                $('#customPathField').show();
            } else {
                $('#customPathField').hide();
            }
        });
    });
    
    function handleSaveFormat(e) {
        e.preventDefault();
        let selectedPath = $('#saveLocation').val();
        let customPath = $('#customPath').val();
        const formData = {
            file_format: $('input[name="file_format"]:checked').val(),
            save_path: selectedPath === 'custom' ? customPath : selectedPath,
            filename: $('input[name="filename"]').val(),
        };
        console.log("Form Data:", formData); // Debugging
        if (!formData.file_format || !formData.save_path || !formData.filename) {
            displayMessageBox('All fields are required.', 'error');
            return;
        }
        $.ajax({
            url: '/save',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                displayMessageBox(response.message, 'message');
            },
            error: function (response) {
                displayMessageBox(response.responseJSON.error, 'error');
            },
        });
    }
    

    // Toggle additional techniques
    function toggleTechniques() {
        const $additionalTechniques = $('#additionalTechniques');
        $additionalTechniques.toggle();
        this.textContent = $additionalTechniques.is(':visible') ? 'Show Fewer Techniques' : 'Discover More Techniques!';
    }

    function toggleDataOverview() {
        const $dataOverviewSection = $('#dimension_overview');
        $dataOverviewSection.toggleClass('hidden');
        this.textContent = $dataOverviewSection.hasClass('hidden') ? 'Show Data Overview' : 'Hide Data Overview';
        dataOverviewSection.style.marginTop = '20px'; 
    }

    // Display messages
    function displayMessageBox(message, type) {
        $messageContent.text(message);
        $messageBox.css('background-color', type === 'error' ? '#dc3545' : '#28a745').removeClass('hidden');
        setTimeout(hideMessageBox, 3000);
    }

    // Hide message box
    function hideMessageBox() {
        $messageBox.addClass('hidden');
    }

    // Handle AJAX errors
    function handleAjaxError(xhr) {
        $spinner.addClass('hidden');
        displayMessageBox(xhr.responseJSON?.error || 'An error occurred.', 'error');
    }
    function emptyElements(selectors) {
        selectors.forEach(selector => $(selector).empty());
    }
});