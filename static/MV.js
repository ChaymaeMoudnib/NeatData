$(document).ready(function() {

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
                fetchDataOverview();
            },
            error: function(response) {
                displayMessageBox(response.responseJSON?.error || "Unknown error", 'error');
            }
        });
    });
    let toggleDataOverviewBtn = document.getElementById('toggleDataOverview');
    if (toggleDataOverviewBtn) {
        toggleDataOverviewBtn.addEventListener('click', function () {
            var dataOverviewSection = document.getElementById('dataOverview');
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

    let toggleTechniquesBtn = document.getElementById('toggleTechniques');
    if (toggleTechniquesBtn) {
        toggleTechniquesBtn.addEventListener('click', function() {
            var additionalTechniques = document.getElementById('additionalTechniques');
            if (additionalTechniques.style.display === 'none') {
                additionalTechniques.style.display = 'block';
                this.textContent = 'Show Fewer Techniques';
            } else {
                additionalTechniques.style.display = 'none';
                this.textContent = 'Discover More Techniques!';
            }
        });
    }
});
$(document).ready(function () {
    $('#saveLocation').on('change', function () {
        if ($(this).val() === 'custom') {
            $('#customPathField').show();
        } else {
            $('#customPathField').hide();
        }
    });

    $('#saveFormatForm').on('submit', function (e) {
        e.preventDefault();
        const fileFormat = $('input[name="file_format"]:checked').val();
        const saveLocation = $('#saveLocation').val();
        const filename = $('#filename').val();
        let savePath = saveLocation;

        if (saveLocation === 'custom') {
            savePath = $('#customPath').val();
            if (!savePath) {
                displayMessageBox('Please provide a valid custom path.', 'error');
                return;
            }
        }
        if (!filename) {
            displayMessageBox('Please enter a filename.', 'error');
            return;
        }

        const formData = {
            file_format: fileFormat,
            save_path: savePath,
            filename: filename
        };

        $.ajax({
            url: '/save',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function (response) {
                displayMessageBox(response.message);
                displayDownloadLink(response.download_url);
            },
            error: function (response) {
                displayMessageBox(response.responseJSON.error, 'error'); // Show error message
            }
        });
    });
});
function displayDownloadLink(link) {
    const linkBox = document.getElementById('downloadLinkBox');
    const linkContent = document.getElementById('downloadLinkContent');
    linkContent.innerHTML = "";
    const linkElement = document.createElement('a');
    linkElement.href = link;
    linkElement.textContent = "Click here to download your file";
    linkElement.target = "_blank"; // Open in new tab
    linkElement.classList.add("link-style");
    linkContent.appendChild(linkElement);
    linkBox.style.backgroundColor = '#007bff'; // Blue for link box
    linkBox.style.color = '#ffffff'; // White text color
    linkBox.style.padding = '15px'; // Padding for the link box
    linkBox.style.borderRadius = '5px'; // Rounded corners
    linkBox.classList.remove('hidden');
    setTimeout(() => {
        linkBox.classList.add('hidden');
    }, 10000);
}

///normal message box
function displayMessageBox(message, type) {
    const messageBox = document.getElementById('messageBox');
    const messageContent = document.getElementById('messageContent');
    const messageButton = document.getElementById('messageButton');
    messageContent.innerHTML = message;
    if (type === 'error') {
        messageBox.style.backgroundColor = '#dc3545'; // Red for error
    } else if (type === 'message') {
        messageBox.style.backgroundColor = '#28a745'; // Green for success
    }
    messageBox.classList.remove('hidden');
    messageButton.removeEventListener('click', hideMessageBox);
    messageButton.addEventListener('click', hideMessageBox);
    setTimeout(hideMessageBox, 5000); 
}

function hideMessageBox() {
    document.getElementById('messageBox').classList.add('hidden');
}

function fetchDataOverview() {
    var missingColor = $('#missingColor').val();
    var presentColor = $('#presentColor').val();
    
    $.ajax({
        url: '/data_overview',
        type: 'GET',
        data: {
            missingColor: missingColor,
            presentColor: presentColor,
            filePath: uploadedFilePath // Pass uploaded file path
        },
        success: function(response) {
            console.log(response);
            $('#missingDataTable').html(response.missing_data_table);
            $('#sampleData').html(response.sample_data);
            $('#missingValuesPlot').attr('src', '/static/images/' + response.missing_values_plot).removeClass('hidden');
        },
        error: function(xhr, status, error) {
            displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
        }
    });
}

$(document).ready(function() {
    $('#processForm').on('submit', function(e) {
        e.preventDefault();

        var formData = {
            choice: $('input[name="choice"]:checked').val(),
            columns: $('input[name="columns"]').val(),
            impute_choice: $('input[name="impute_choice"]:checked').val(),
            impute_params: {}
        };

        switch (formData.impute_choice) {
            case 'mean_median_mode':
                formData.impute_params.strategy = $('input[name="strategy"]:checked').val();
                break;
            case 'knn':
                formData.impute_params.n_neighbors = parseInt($('input[name="n_neighbors"]').val()) || 5;
                formData.impute_params.metric = $('input[name="metric"]:checked').val();
                break;
            case 'mice':
                formData.impute_params.n_imputations = parseInt($('input[name="n_imputations"]').val()) || 10;
                formData.impute_params.max_iter = parseInt($('input[name="max_iter"]').val()) || 10;
                formData.impute_params.method = $('input[name="method"]:checked').val();
                break;
            case 'regression':
                formData.impute_params.model = $('input[name="regression_model"]:checked').val();
                formData.impute_params.predictors = $('input[name="predictors"]').val()
                    ? $('input[name="predictors"]').val().split(',').map(s => s.trim()).filter(Boolean)
                    : [];
                break;
            case 'probability':
                formData.impute_params.distribution = $('input[name="distribution"]:checked').val();
                formData.impute_params.parameters = $('input[name="parameters"]').val()
                    ? $('input[name="parameters"]').val().split(',').map(Number).filter(n => !isNaN(n))
                    : [];
                break;
            case 'autoencoder':
                formData.impute_params.hidden_layers = parseInt($('input[name="hidden_layers"]').val()) || 2;
                formData.impute_params.activation = $('input[name="activation"]:checked').val();
                formData.impute_params.epochs = parseInt($('input[name="epochs"]').val()) || 50;
                formData.impute_params.learning_rate = parseFloat($('input[name="learning_rate"]').val()) || 0.001;
                break;
        }

        console.log("Form Data Sent:", formData);

        $.ajax({
            url: '/process',
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                displayMessageBox(response.message, 'message');
                $('#saveOptions').removeClass('hidden');
                $('#missingValuesContainer').html(response.missing_data_table || "<p>No missing data found.</p>").removeClass('hidden');
            },
            error: function(response) {
                displayMessageBox(response.responseJSON?.error || "Unknown error", 'error');
                $('#missingValuesContainer').html(response.responseJSON?.missing_values_table || "<p>Error retrieving missing values.</p>").removeClass('hidden');
            }
        });
    });

    $('input[name="choice"]').change(function() {
        let show = $(this).val() === '3';
        $('#imputationMethods').toggleClass('hidden', !show);
        $('.hidden-params').addClass('hidden');
    });

    $('input[name="impute_choice"]').change(function() {
        $('.hidden-params').addClass('hidden');
        $('#' + $(this).val() + 'Params').removeClass('hidden');
    });
});

$('#resetButton').on('click', function() {
    $.ajax({
        url: '/reset',
        type: 'POST',
        success: function() {
            // Reset the upload form
            displayMessageBox('Form reset successfully.', 'message');
            $('#uploadForm')[0].reset();
            $('#fileInput').val(''); // This line clears the file input
            $('#filePlaceholder').text('Choose a File'); // Reset the placeholder text
            $('#dataOverview').addClass('hidden').find('pre, div').text('');
            $('#toggleDataOverview').text('Show Data Overview'); 
            $('#missingValuesPlot').addClass('hidden').attr('src', '');
            $('#processForm')[0].reset();
            $('#imputationMethods').addClass('hidden');
            $('.hidden-params').addClass('hidden');
            $('#missingValuesContainer').addClass('hidden').html('');
            $('#saveOptions').addClass('hidden');
            $('#saveFormatForm')[0].reset();
            $('#customPathField').hide();
            $('#uploadMessage').text('').removeClass('error message');
            $('#saveMessage').text('').removeClass('error message');
            $('#plotCustomizationForm')[0].reset();
            $('#additionalTechniques').hide();
            $('#toggleTechniques').text('Discover More Techniques!');
            uploadedFilePath = '';
            displayMessageBox('Form reset successfully.', 'message');
        },
        error: function(xhr) {
            displayMessageBox("An error occurred: " + xhr.responseText, 'error');
        }
    });
});

$('#plotCustomizationForm').on('submit', function(e) {
    e.preventDefault();
    var plotData = {
        colorMap: $('#colorMap').val(),
        plotWidth: $('#plotWidth').val(),
        plotHeight: $('#plotHeight').val(),
        missingColor: $('#missingColor').val(),
        presentColor: $('#presentColor').val()
    };

    console.log("Plot Customization Data:", plotData);

    $.ajax({
        url: '/customize_plot',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(plotData),
        success: function(response) {
            console.log("Plot Response:", response);
            var timestamp = new Date().getTime();
            $('#missingValuesPlot').attr('src', '/static/images/' + response.missing_values_plot + '?t=' + timestamp).removeClass('hidden');
        },
        error: function(xhr, status, error) {
            console.error(xhr.responseText);
            displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
        }
    });
});

