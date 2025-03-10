document.addEventListener('DOMContentLoaded', function () {
    const uploadForm = document.getElementById('uploadForm');
    const resetButton = document.getElementById('resetButton');
    const detectOutliersButton = document.getElementById('detectOutliers');
    const applyFilterButton = document.getElementById('applyFilter');
    const saveDataButton = document.getElementById('saveData');
    const columnSelect = document.getElementById('columnSelect');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const outlierTableBody = document.getElementById('outlierTableBody');
    const boxplotImage = document.getElementById('boxplotImage');
    const boxplotContainer = document.getElementById('boxplotContainer');
    const $spinner = $('#spinner');
    
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
    uploadForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(uploadForm);
    
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                displayMessageBox(response.message, 'message');
                detectOutliers()
            
            },                    
            error: function(xhr) {
                displayMessageBox(response.responseJSON?.error || "Unknown error", 'error');
            }
        });
    });
    function fetchColumns() {
        console.log('Fetching columns...');
        showSpinner(); // Show spinner while fetching columns
    
        $.ajax({
            url: '/get-columns', // Endpoint to fetch columns
            type: 'GET', // HTTP method
            dataType: 'json', // Expected response type
            success: function(data) {
                hideSpinner(); // Hide spinner after fetching columns
                console.log('Columns data received:', data);
    
                if (data && Array.isArray(data.columns)) {
                    populateColumnSelect(data.columns); // Populate the dropdown
                } else {
                    console.error('Invalid columns structure in response:', data);
                    displayMessageBox("Invalid columns structure received.", 'error');
                }
            },
            error: function(xhr, status, error) {
                hideSpinner(); // Hide spinner in case of error
                console.error('Error fetching columns:', error);
                displayMessageBox("Error fetching columns: " + xhr.responseText, 'error');
            }
        });
    }
    
    function populateColumnSelect(columns) {
        const columnSelect = document.getElementById('columnSelect');
        if (!columnSelect) {
            console.error('Column select element not found!');
            return;
        }
        columnSelect.innerHTML = '';
        if (!columns || !Array.isArray(columns)) {
            console.error('Invalid columns input:', columns);
            displayMessageBox("Invalid columns data received.", 'error');
            return;
        }
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Select a column';
        columnSelect.appendChild(defaultOption);
        columns.forEach(column => {
            const option = document.createElement('option');
            option.value = column;
            option.textContent = column;
            columnSelect.appendChild(option);
        });
        console.log('Column select populated with:', columns);
    }
    

    resetButton.addEventListener('click', function () {
        $.ajax({
            url: '/reset',
            type: 'POST',
            success: function () {
                displayMessageBox('Form reset successfully.', 'message');
                $('#fileInput').val(''); // This line clears the file input
                $('#filePlaceholder').text('Choose a File'); // Reset the placeholder text
                $('#uploadForm')[0].reset();
                $('#columnSelect').empty(); // Clear column dropdown
                $('#maxValue').val(''); // Clear min value input
                $('#minValue').val(''); // Clear max value input
                $('#saveOptions').addClass('hidden'); // Hide save options
                $('#outlierTableContainer').addClass('d-none'); // Hide the outlier table
$('#outlierTableBody').empty(); // Clear the table
$('#boxplotContainer').addClass('d-none'); // Hide the boxplot image
           $('#boxplotImage').attr('src', ''); // Clear the image
                fileNameDisplay.textContent = ''; // Clear file name display  
            },
            error: function (xhr) {
                displayMessageBox("An error occurred: " + xhr.responseText, 'error');
            }
        });
    });

    function detectOutliers() {
        showSpinner(); 
        fetch('/detect-outliers', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            hideSpinner(); 
            console.log("Outliers data:", data);
            if (data.outlier_columns) {
                displayMessageBox("Outliers detected successfully!", 'message');
                document.getElementById('outlierTableContainer').classList.remove('d-none'); // Show the table
                populateOutlierTable(data);
                fetchColumns(); // Fetch columns after detecting outliers
            } else {
                displayMessageBox("Error detecting outliers: " + data.error, 'error');
            }
        })
        .catch(error => {
            hideSpinner(); 
            displayMessageBox("An error occurred: " + error.message, 'error');
        });
    }    
    detectOutliersButton.addEventListener('click', detectOutliers);

    
    // Modify fetchColumns to return a Promise
    function fetchColumns() {
        return new Promise((resolve, reject) => {
            console.log('Fetching columns...');
            showSpinner(); // Show spinner while fetching columns
        
            $.ajax({
                url: '/get-columns', 
                type: 'GET',
                dataType: 'json',
                success: function(data) {
                    hideSpinner();
                    console.log('Columns data received:', data);
        
                    if (data && Array.isArray(data.columns)) {
                        populateColumnSelect(data.columns);
                        resolve(data.columns);  // Resolve the promise with columns
                    } else {
                        console.error('Invalid columns structure in response:', data);
                        displayMessageBox("Invalid columns structure received.", 'error');
                        reject("Invalid response structure");
                    }
                },
                error: function(xhr, status, error) {
                    hideSpinner();
                    console.error('Error fetching columns:', error);
                    displayMessageBox("Error fetching columns: " + xhr.responseText, 'error');
                    reject(error);
                }
            });
        });
    }    

    document.getElementById('saveLocation').addEventListener('change', function () {
        const customPathField = document.getElementById('customPathField');
        customPathField.style.display = this.value === 'custom' ? 'block' : 'none';
    });
    function populateOutlierTable(data) {
        outlierTableBody.innerHTML = ''; // Clear the table
        data.outlier_columns.forEach(column => {
            const row = document.createElement('tr');
            const columnCell = document.createElement('td');
            columnCell.textContent = column;
            row.appendChild(columnCell);

            const outliersCell = document.createElement('td');
            outliersCell.textContent = data.outliers_values[column].join(', ');
            row.appendChild(outliersCell);

            outlierTableBody.appendChild(row);
        });
    }

    outlierTableBody.addEventListener('click', function(event) {
        if (event.target.closest('tr')) {
            const selectedRow = event.target.closest('tr');
            const selectedColumn = selectedRow.cells[0].textContent; 
            fetch('/get-boxplot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ column: selectedColumn })
            })
            .then(response => response.blob())
            .then(blob => {
                const imageUrl = URL.createObjectURL(blob);
                boxplotImage.src = imageUrl; // Update boxplot image URL
                boxplotContainer.classList.remove('d-none'); // Show the boxplot container
            })
            .catch(error => {
                displayMessageBox("An error occurred: " + error.message, 'error');
            });
        }
    });

    document.getElementById('applyFilter').addEventListener('click', function () {
        const minInput = document.getElementById('minValue').value.trim().toLowerCase();
        const maxInput = document.getElementById('maxValue').value.trim().toLowerCase();
        const selectedColumn = columnSelect.value;
    
        // If input is empty, set to "none"
        const minValue = minInput === "" || minInput === "none" ? "none" : parseFloat(minInput);
        const maxValue = maxInput === "" || maxInput === "none" ? "none" : parseFloat(maxInput);
    
        if ((minValue !== "none" && isNaN(minValue)) || (maxValue !== "none" && isNaN(maxValue))) {
            displayMessageBox("Please enter valid numeric values or 'none' to ignore a limit.", 'error');
            return;
        }
    
        fetch('/filter-outliers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ column: selectedColumn, min_value: minValue, max_value: maxValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                displayMessageBox("Filter applied successfully!", 'message');
            } else {
                displayMessageBox("Error applying filter: " + data.error, 'error');
            }
        })
        .catch(error => {
            displayMessageBox("An error occurred: " + error.message, 'error');
        });
    });
    saveDataButton.addEventListener('click', function () {
        $('#saveOptions').removeClass('hidden')
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
    
function populateOutlierTable(data) {
    outlierTableBody.innerHTML = ''; // Clear the table
    data.outlier_columns.forEach(column => {
        const row = document.createElement('tr');
        const columnCell = document.createElement('td');
        columnCell.textContent = column;
        row.appendChild(columnCell);

        const outliersCell = document.createElement('td');
        outliersCell.textContent = data.outliers_values[column].join(', ');
        row.appendChild(outliersCell);

        outlierTableBody.appendChild(row);
    });
}
});
