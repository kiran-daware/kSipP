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
    downloadLink.href = `xml/${xmlName}`;
    downloadLink.download = xmlName; 
    downloadLink.className = 'download-button';
    downloadLink.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" height="16" width="16" viewBox="0 0 512 512"><!--!Font Awesome Free 6.6.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path fill="currentColor" d="M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 242.7-73.4-73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l128 128c12.5 12.5 32.8 12.5 45.3 0l128-128c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L288 274.7 288 32zM64 352c-35.3 0-64 28.7-64 64l0 32c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-32c0-35.3-28.7-64-64-64l-101.5 0-45.3 45.3c-25 25-65.5 25-90.5 0L165.5 352 64 352zm368 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"/></svg>`;

    listItem.setAttribute('data-filename', xmlName);
    listItem.classList.add('show-flow');

    // // View Diagram link
    // const viewLink = document.createElement('a');
    // viewLink.href = `#`;
    // viewLink.textContent = `view flow`;
    // viewLink.className = 'view-link';
    // viewLink.setAttribute('data-filename', xmlName);
    // Event listener to highlight the selected item
    listItem.addEventListener('click', () => {
        document.querySelectorAll('li').forEach(li => li.classList.remove('selected'));
        listItem.classList.add('selected');
    });
    // Append links to the list item
    listItem.appendChild(spanElm);
    listItem.appendChild(downloadLink);
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
    const response = await fetch(`https://kiran-daware.github.io/sipp-xml/xml/${fileName}`);
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