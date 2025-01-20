$(document).ready(function () {
    $('#uploadForm').submit(function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                $('#visualizationOptions').removeClass('d-none');
                alert('Dataset uploaded successfully. Available columns: ' + response.columns.join(', '));
            },
            error: function () {
                alert('Error uploading dataset.');
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

    $('#visualizationForm').submit(function (e) {
        e.preventDefault();

        const formData = {
            filename: $('#fileInput').val().split('\\').pop(),
            columns: $('#columns').val(),
            chartType: $('#chartType').val(),
            chartWidth: $('#chartWidth').val(),
            chartHeight: $('#chartHeight').val(),
            backgroundColor: $('#backgroundColor').val(),
            lineColor: $('#lineColor').val()
        };
    
        $.ajax({
            url: '/visualise',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                const chartCanvas = $('#chartCanvas')[0].getContext('2d');
                const img = new Image();
                img.onload = function () {
                    chartCanvas.drawImage(img, 0, 0);
                };
                img.src = response.imagePath;
                $('#visualizationOutput').removeClass('d-none');
                $('#downloadImage').attr('href', '/download/visualization.png');
            },
            error: function () {
                alert('Error generating visualization.');
            }
        });
    });
});
