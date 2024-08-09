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

function parseXML(xmlString) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlString, "text/xml");
    return xmlDoc;
}

function renderDiagram(umlText) {
    const diagram = Diagram.parse(umlText);
    diagram.drawSVG('flow-diagram', {theme: 'simple'});
}

async function fetchXMLFile(fileName) {
    const response = await fetch(`/xml/${fileName}`);
    if (!response.ok) {
        throw new Error(`Could not fetch ${fileName}`);
    }
    const xmlText = await response.text();
    return xmlText;
}

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



document.addEventListener('click', async (event) => {
    if (event.target && event.target.id === 'show-flow-button') {
        var modal = document.getElementById('flow-modal');
        var span = document.getElementsByClassName('close')[0];

            modal.style.display = 'block';

        span.onclick = function() {
            modal.style.display = 'none';
        }

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
    }}
});
