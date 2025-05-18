// script.js

document.getElementById('crimeReportForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = {
        firNo: document.getElementById('firNo').value,
        district: document.getElementById('district').value,
        date: document.getElementById('date').value,
        day: document.getElementById('day').value,
        dateOfOccurrence: document.getElementById('dateOfOccurrence').value,
        placeOfOccurrence: document.getElementById('placeOfOccurrence').value,
        name: document.getElementById('name').value,
        dob: document.getElementById('dob').value,
        nationality: document.getElementById('nationality').value,
        occupation: document.getElementById('occupation').value,
        address: document.getElementById('address').value,
        reportedCrime: document.getElementById('reportedCrime').value,
        propertiesInvolved: document.getElementById('propertiesInvolved').value
    };

    function sanitizeId(text) {
        return text.replace(/\W+/g, '_'); // Replace non-alphanumeric chars with underscores
    }

    function addIpcSectionsCheckboxes(ipcSections) {
        const container = document.getElementById('ipc-sections-container');
        container.innerHTML = ''; // Clear existing content

        ipcSections.forEach(section => {
            const safeId = sanitizeId(section.section + '_' + section.title);

            // Create checkbox
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input';
            checkbox.id = safeId;
            checkbox.name = 'ipcSections';
            checkbox.value = `${section.section} - ${section.title}`;

            // Create label
            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = safeId;
            label.textContent = `${section.section} - ${section.title}`;

            // Wrap checkbox and label in a div
            const wrapper = document.createElement('div');
            wrapper.className = 'form-check mb-1';
            wrapper.appendChild(checkbox);
            wrapper.appendChild(label);

            container.appendChild(wrapper);
        });
    }

    // New function to add BNS sections checkboxes
    function addBnsSectionsCheckboxes(bnsSections) {
        const container = document.getElementById('bns-sections-container');
        container.innerHTML = ''; // Clear existing content

        bnsSections.forEach(section => {
            const safeId = sanitizeId('bns_' + section.section + '_' + section.title);

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input';
            checkbox.id = safeId;
            checkbox.name = 'bnsSections';
            checkbox.value = `${section.section} - ${section.title}`;

            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = safeId;
            label.textContent = `${section.section} - ${section.title}`;

            const wrapper = document.createElement('div');
            wrapper.className = 'form-check mb-1';
            wrapper.appendChild(checkbox);
            wrapper.appendChild(label);

            container.appendChild(wrapper);
        });
    }

    // Show loading animation
    var loadingElement = document.getElementById('loadingAnimation');
    loadingElement.style.display = 'block';

    fetch('/process_reported_crime', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        loadingElement.style.display = 'none';
        console.log("Received result from server:", data.result);

        document.getElementById('firNoForIpc').value = formData.firNo;

        if (data.status === 'success') {
            const result = data.result;

            // Handle both direct array and object with ipc/bns arrays
            if (Array.isArray(result)) {
                // Direct IPC array response
                addIpcSectionsCheckboxes(result);

                var output = document.getElementById('reportOutput');
                if (output) {
                    output.innerHTML = '<h4>Applicable IPC Sections are as follows:</h4><ul>' +
                        result.map(s => `<li>${s.section} - ${s.title}</li>`).join('') + '</ul>';
                    output.style.display = 'block';
                }
            } else if (typeof result === 'object' && result !== null) {
                const ipcArray = result.ipc || [];
                const bnsArray = result.bns || [];

                // Remove duplicates by section for IPC & BNS
                const uniqueIpc = [...new Map(ipcArray.map(item => [item.section, item])).values()];
                const uniqueBns = [...new Map(bnsArray.map(item => [item.section, item])).values()];

                if (uniqueIpc.length > 0) {
                    addIpcSectionsCheckboxes(uniqueIpc);

                    var ipcOutput = document.getElementById('reportOutputIpc');
                    if (ipcOutput) {
                        ipcOutput.innerHTML = '<h4>Applicable IPC Sections are as follows:</h4><ul>' +
                            uniqueIpc.map(s => `<li>${s.section} - ${s.title}</li>`).join('') + '</ul>';
                        ipcOutput.style.display = 'block';
                    }
                } else {
                    document.getElementById('ipc-sections-container').innerHTML = '<p>No IPC sections identified.</p>';
                }

                if (uniqueBns.length > 0) {
                    addBnsSectionsCheckboxes(uniqueBns);

                    var bnsOutput = document.getElementById('reportOutputBns');
                    if (bnsOutput) {
                        bnsOutput.innerHTML = '<h4>Applicable BNS Sections are as follows:</h4><ul>' +
                            uniqueBns.map(s => `<li>${s.section} - ${s.title}</li>`).join('') + '</ul>';
                        bnsOutput.style.display = 'block';
                    }
                } else {
                    document.getElementById('bns-sections-container').innerHTML = '<p>No BNS sections identified.</p>';
                }
            } else {
                console.error("Expected array or object with IPC/BNS arrays but got:", result);
                alert('Unexpected response format from server.');
            }
        } else {
            alert('Failed to get IPC sections: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        loadingElement.style.display = 'none';
        console.error('Error:', error);
        alert('Error processing request. Check console for details.');
    });
});

// Handle the IPC sections form submission
document.getElementById('ipcSectionsForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var firNo = document.getElementById('firNoForIpc').value;
    var checkedIpcSections = Array.from(document.querySelectorAll('#ipcSectionsForm input[name="ipcSections"]:checked'))
        .map(checkbox => checkbox.value);

    fetch('/submit_ipc_sections', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            firNo: firNo,
            ipcSections: checkedIpcSections.join(', ')
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success') {
            window.location.href = `/display_fir/${firNo}`;
        } else {
            alert('Failed to submit IPC Sections: ' + data.message);
            console.error('Failed to submit IPC Sections:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting IPC Sections. Check console.');
    });
});




    // function addIpcSectionsCheckboxes(ipcSections) {
    //     const container = document.getElementById('ipc-sections-container'); // Replace with your actual container ID
    //     container.innerHTML = ''; // Clear existing content
    
    //     ipcSections.forEach(section => {
    //         const checkbox = document.createElement('input');
    //         checkbox.type = 'checkbox';
    //         checkbox.name = 'ipcSections';
    //         checkbox.value = section;
    
    //         const label = document.createElement('label');
    //         label.appendChild(checkbox);
    //         label.appendChild(document.createTextNode(section));
    
    //         container.appendChild(label);
    //         container.appendChild(document.createElement('br'));
    //     });
    // }    


