const uacXmlList = document.getElementById('uac-list');
const uasXmlList = document.getElementById('uas-list');

function createXmlListItem(xmlName){
    const listItem = document.createElement('li');
    const spanElm = document.createElement('span');
    spanElm.textContent = `${xmlName} `;
    spanElm.setAttribute('data-filename', xmlName);
    spanElm.classList.add('show-flow');
    // Download link
    const downloadLink = document.createElement('a');
    downloadLink.href = `/xml/${xmlName}`;
    downloadLink.download = xmlName; 
    downloadLink.className = 'xml-li-button';
    downloadLink.title = 'Download';
    downloadLink.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" height="16px" width="16px" fill="currentColor"><path d="M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 242.7-73.4-73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l128 128c12.5 12.5 32.8 12.5 45.3 0l128-128c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L288 274.7 288 32zM64 352c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-101.5 0-45.3 45.3c-25 25-65.5 25-90.5 0L165.5 352 64 352zm368 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"/></svg>`;

    // Edit Link
    const editLink = document.createElement('a');
    editLink.href=`/edit-xml/?xml=${xmlName}&back=xml-list`;
    editLink.className = 'xml-li-button';
    editLink.title = 'Edit';
    editLink.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" height="16px" width="16px" fill="currentColor"><path d="M471.6 21.7c-21.9-21.9-57.3-21.9-79.2 0L362.3 51.7l97.9 97.9 30.1-30.1c21.9-21.9 21.9-57.3 0-79.2L471.6 21.7zm-299.2 220c-6.1 6.1-10.8 13.6-13.5 21.9l-29.6 88.8c-2.9 8.6-.6 18.1 5.8 24.6s15.9 8.7 24.6 5.8l88.8-29.6c8.2-2.7 15.7-7.4 21.9-13.5L437.7 172.3 339.7 74.3 172.4 241.7zM96 64C43 64 0 107 0 160L0 416c0 53 43 96 96 96l256 0c53 0 96-43 96-96l0-96c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7-14.3 32-32 32L96 448c-17.7 0-32-14.3-32-32l0-256c0-17.7 14.3-32 32-32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L96 64z"/></svg>`;

    // Delete button 
    const deleteXml = document.createElement('a');
    deleteXml.href = `/xml-list/?delete=${xmlName}`;
    deleteXml.className = 'xml-li-button';
    deleteXml.title = 'Delete';
    deleteXml.onclick = function() {
        return confirm(`Are you sure you want to delete this file: ${xmlName}?`);
    };
    deleteXml.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" height="16px" width="16px" fill="currentColor"><path d="M135.2 17.7L128 32 32 32C14.3 32 0 46.3 0 64S14.3 96 32 96l384 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-96 0-7.2-14.3C307.4 6.8 296.3 0 284.2 0L163.8 0c-12.1 0-23.2 6.8-28.6 17.7zM416 128L32 128 53.2 467c1.6 25.3 22.6 45 47.9 45l245.8 0c25.3 0 46.3-19.7 47.9-45L416 128z"/></svg>`;



    listItem.setAttribute('data-filename', xmlName);
    listItem.classList.add('show-flow');
    listItem.addEventListener('click', () => {
        document.querySelectorAll('li').forEach(li => li.classList.remove('selected'));
        listItem.classList.add('selected');
    });

    // Append links to the list item
    listItem.appendChild(spanElm);
    listItem.appendChild(downloadLink);
    listItem.appendChild(editLink);
    listItem.appendChild(deleteXml);
    // listItem.appendChild(viewLink);
    return listItem;
};

uacXmlFiles.forEach(file => {
    const listItem = createXmlListItem(file);
    uacXmlList.appendChild(listItem);
});
uasXmlFiles.forEach(file => {
    const listItem = createXmlListItem(file);
    uasXmlList.appendChild(listItem);
});


// Event listener for View Diagram links
document.addEventListener('click', async (event) => {
    if (event.target && event.target.classList.contains('show-flow')) {
        event.preventDefault();
        // Clear the old diagram
        const container = document.getElementById('flow-diagram');
        container.innerHTML = '';

        const fileName = event.target.getAttribute('data-filename');
        try {
            const xmlText = await fetchXMLFile(fileName);
            const xmlDoc = parseXML(xmlText);
            const umlText = generateUMLText(xmlDoc, fileName);
            renderDiagram(umlText);
        } catch (error) {
            console.error("Error:", error);
            container.innerHTML = `<br>${error}`
        }
    }
});

async function fetchXMLFile(fileName) {
    const response = await fetch(`/xml/${fileName}`);
    if (!response.ok) {
        throw new Error(`Could not fetch ${fileName}`);
    }
    const xmlText = await response.text();
    return xmlText;
}

function parseXML(xmlString) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlString, "text/xml");
    return xmlDoc;
}


function extractMessageType(message) {
    // Match SIP request methods
    const requestMatch = message.match(/^\s*(INVITE|ACK|BYE|CANCEL|OPTIONS|REGISTER|PRACK|SUBSCRIBE|NOTIFY|PUBLISH|INFO|REFER|MESSAGE|UPDATE)\s+/m);
    // Match SIP response codes
    const responseMatch = message.match(/^\s*SIP\/\d\.\d\s*(\d{3})\s+/m);

    if (requestMatch) {
        return requestMatch[1];
    } else if (responseMatch) {
        return `${responseMatch[1]}`;
    } else {
        return 'Unknown';
    }
}


function generateUMLText(xmlDoc, fileName) {
    let umlText = `
participant ${fileName} as thisXml
participant farEnd
`;
    const allElements = xmlDoc.getElementsByTagName("*"); // Get all elements
    const sipMessages = [];

    // Iterate over all elements and filter `send` and `recv`
    Array.from(allElements).forEach(element => {
        if (element.tagName === "send" || element.tagName === "recv") {
            sipMessages.push(element);
        }
    });


    sipMessages.forEach(messageElement => {
        const tagName = messageElement.tagName;
        const from = tagName === "send" ? "thisXml" : "farEnd";
        const to = tagName === "send" ? "farEnd" : "thisXml";

        if (tagName === "send") {
            const message = messageElement.textContent.trim();
            const messageType = extractMessageType(message);
            umlText += `${from} -> ${to}: send    ${messageType}\n`;
        } else if (tagName === "recv") {
            const request = messageElement.getAttribute("request");
            const response = messageElement.getAttribute("response");
            let statusCodeAndText = '';

            if (request) {
                statusCodeAndText = request;
            } else if (response) {
                statusCodeAndText = response;
            }

            umlText += `${from} -> ${to}: recv    ${statusCodeAndText}\n`;
        }
    });
    return umlText;
}

function renderDiagram(umlText) {
    const diagram = Diagram.parse(umlText);
    diagram.drawSVG('flow-diagram', {theme: 'simple'});
}


// XML Upload modal
document.addEventListener('DOMContentLoaded', function() {     
    // Check if modal needs to be opened automatically
    // Add close functionality
    var modal = document.getElementById('upload-modal');
    var span = document.getElementsByClassName('close')[0];

    span.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});

// Open modal on button click
document.addEventListener('click', async (event) => {
    if (event.target && event.target.id === 'upload-xml-b') {
        document.getElementById('upload-modal').style.display = 'block';
    }
});

