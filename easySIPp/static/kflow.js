function generateUMLText(xmlDoc, fileName) {
    let umlText = '';
    if(fileName.startsWith("uac")){
    umlText = `
participant ${fileName} as thisXml
participant farEnd
`;}
    else if(fileName.startsWith("uas")){
    umlText = `
participant farEnd
participant ${fileName} as thisXml
`;}
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

function renderDiagram(umlText, container) {
    const diagram = Diagram.parse(umlText);
    diagram.drawSVG(container, {theme: 'simple'});
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
        const container = document.getElementById('flow-diagram1');
        const container2 = document.getElementById('flow-diagram2');
        container.innerHTML = '';
        container2.innerHTML = '';

        const fileName = event.target.getAttribute('data-filename');
        const filename2 = event.target.getAttribute('data-filename2');

        const renderFile = async (filename, container) => {
            try {
                const xmlText = await fetchXMLFile(filename);
                const xmlDoc = parseXML(xmlText);
                const umlText = generateUMLText(xmlDoc, filename);
                renderDiagram(umlText, container);
            } catch (error) {
                console.error("Error:", error);
                container.innerHTML = `<br>${error}`;
            }
        };

        // Render diagram(s) conditionally
        if (fileName) {
            await renderFile(fileName, container);
        }
        if (filename2) {
            await renderFile(filename2, container2);
        }
        if (!filename2) { container2.style.display ="none" }

    }
});


document.addEventListener('click', async (event) => {
    if (event.target && event.target.classList.contains('show-flow')) {
        const modal = document.getElementById('flow-modal');
        const span = document.getElementsByClassName('close')[0];

        modal.style.display = 'block';

        span.onclick = function () {
            modal.style.display = 'none';
        };

        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    }
});
