$(document).ready(function () {
    let uploadedFilePath = ''; // Store uploaded file path globally
    $('#saveOptions').addClass("hidden");

    function showSpinner() {
        const spinner = $('.spinner');
        const functionalitySection = $('.functionality-section');

        if (spinner.length && functionalitySection.length) {
            const rect = functionalitySection[0].getBoundingClientRect();
            spinner.css({
                position: 'absolute',
                top: `${rect.top}px`,
                left: `${rect.left}px`,
                width: `${rect.width}px`,
                height: `${rect.height}px`
            }).removeClass('hidden');
        }
    }

    function hideSpinner() {
        $('.spinner').addClass('hidden');
    }

    function displayMessageBox(message, type) {
        const messageBox = $('#messageBox');
        $('#messageContent').html(message); // Allow HTML content
        messageBox.css('background-color', type === 'error' ? '#dc3545' : '#28a745')
            .removeClass('hidden');

        setTimeout(() => messageBox.addClass('hidden'), 3000);
    }

    function displayDownloadLink(link) {
        const linkBox = $('#downloadLinkBox');
        const linkContent = $('#downloadLinkContent');

        // Clear previous content
        linkContent.empty();

        // Create link element
        const linkElement = $('<a></a>').attr({
            href: link,
            download: true // Ensures download attribute is set
        }).text("Click here to download your file").addClass("link-style");

        // Append link to the link content
        linkContent.append(linkElement);

        // Apply styles to the link box
        linkBox.css({
            backgroundColor: '#007bff', // Blue for link box
            color: '#ffffff', // White text color
            padding: '15px', // Padding for the link box
            borderRadius: '5px' // Rounded corners
        }).removeClass('hidden'); // Show the link box

        // Automatically hide after 10 seconds
        setTimeout(() => {
            linkBox.addClass('hidden');
        }, 10000);
    }

    $('#messageButton').on('click', () => $('#messageBox').addClass('hidden'));

    function populateColumns() {
        $.getJSON('/get_columns')
            .done(function (data) {
                const columnSelect = $('#target_column');
                columnSelect.empty();

                if (data.columns && data.columns.length) {
                    data.columns.forEach(column => columnSelect.append(new Option(column, column)));
                } else {
                    columnSelect.append(new Option("No columns available", ""));
                }
            })
            .fail(xhr => console.error("Failed to load columns:", xhr.responseText));
    }

    function fetchBeforeTable() {
        $.post('/before')
            .done(response => {
                if (response.table_before?.length) {
                    let tableBeforeHtml = `<h4>Table Before Corrections:</h4><table class='table'><thead><tr>`;
                    Object.keys(response.table_before[0]).forEach(col => tableBeforeHtml += `<th>${col}</th>`);
                    tableBeforeHtml += `</tr></thead><tbody>`;

                    response.table_before.forEach(row => {
                        tableBeforeHtml += "<tr>";
                        Object.values(row).forEach(value => tableBeforeHtml += `<td>${value}</td>`);
                        tableBeforeHtml += "</tr>";
                    });

                    $('#tablebef').html(tableBeforeHtml).show();
                } else {
                    $('#tablebef').html('<p>No data available for the overview.</p>').show();
                }
            })
            .fail(xhr => displayMessageBox('Failed to fetch before table: ' + xhr.responseText, 'error'));
    }

    $('#resetButton').on('click', function () {
        const elementsToReset = [
            'uploadForm',
            'uploadMessage',
            'tablebef',
            'saveOptions',
            'nextAction',
            'correctionResults',
            'dateChoices',
            'correctionsContainer',
            'fileInput'
        ];
        
        // Reset the form
        $('#uploadForm')[0].reset();
        
        // Clear upload message and reset file input placeholder
        $('#uploadMessage').text('');
        $('#filePlaceholder').text("Choose a File");
        $('#tablebef').empty();
        $('#toggleDataOverview').text('Show Data Overview');
        elementsToReset.forEach(id => {
            const element = $('#' + id);
            element.addClass('hidden');
            if (element.is('input, textarea')) {
                element.val('');
            }
        });
        $('#correctionResults').empty();
        displayMessageBox('Form reset successfully.', 'message');
    });
    

    $('#toggleDataOverview').on('click', function () {
        $('#tablebef').toggleClass('hidden'); // Toggle visibility of the table
        const isHidden = $('#tablebef').hasClass('hidden');
        $(this).text(isHidden ? 'Show Data Overview' : 'Hide Data Overview'); // Update button text
    });

    $('#correction_method').on('change', function () {
        $('#dateChoices, #correctionsContainer').addClass('hidden');
        if (this.value === 'modify_date') {
            $('#dateChoices').removeClass('hidden');
        } else if (this.value === 'replace' || this.value === 'remove') {
            $('#correctionsContainer').removeClass('hidden');
        }
    });

    $('#correctionForm').on('submit', function (event) {
        event.preventDefault();
        showSpinner();
        
        $.ajax({
            url: '/correct',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                target_column: $('#target_column').val(),
                corrections: $('#corrections').val(),
                date_format: $('#date_format').val(),
                action: $('#correction_method').val()
            })
        })
            .done(response => {
                hideSpinner();
                $('#saveOptions').removeClass("hidden");
                let tableAfterHtml = "<h4>Table After Corrections:</h4><table class='table'><thead><tr>";
                Object.keys(response.table[0]).forEach(col => tableAfterHtml += `<th>${col}</th>`);
                tableAfterHtml += `</tr></thead><tbody>`;

                response.table.forEach(row => {
                    tableAfterHtml += "<tr>";
                    Object.values(row).forEach(value => tableAfterHtml += `<td>${value}</td>`);
                    tableAfterHtml += "</tr>";
                });
                $('#correctionResults').html(tableAfterHtml).show();
            })
            .fail(xhr => {
                hideSpinner();
                displayMessageBox(xhr.responseJSON?.error || 'An error occurred', 'error');
            });
    });

    $('#fileInput').on('change', function () {
        $('#filePlaceholder').text(this.files.length > 0 ? this.files[0].name : "Choose a File");
    });

    $('#uploadForm').on('submit', function (e) {
        e.preventDefault();
        showSpinner();

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: new FormData(this),
            contentType: false,
            processData: false
        })
            .done(data => {
                hideSpinner();
                if (data.error) {
                    displayMessageBox(data.error, 'error');
                } else {
                    uploadedFilePath = data.file_path;
                    displayMessageBox(data.message, 'message');
                    fetchBeforeTable();
                    populateColumns();
                }
            })
            .fail(xhr => {
                hideSpinner();
                displayMessageBox('An error occurred: ' + xhr.responseText, 'error');
            });
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
                    displayDownloadLink(response.download_url);                },
                error: function (xhr) {
                    displayMessageBox(xhr.responseJSON.error || 'An error occurred while saving.', 'error');
                }
            });
        });
    });
});
