$(document).ready(function () {


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

    document.getElementById("fileInput").addEventListener("change", function () {
        var fileName = this.files.length > 0 ? this.files[0].name : "Choose a File";
        document.getElementById("filePlaceholder").textContent = fileName;
    });
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
        // Toggle additional techniques
        function toggleTechniques() {
            const $additionalTechniques = $('#additionalTechniques');
            $additionalTechniques.toggle();
            this.textContent = $additionalTechniques.is(':visible') ? 'Show Fewer Techniques' : 'Discover More Techniques!';
        }
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










})