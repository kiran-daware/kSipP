//createUAS and othe constants in below function are described in createUACxml.js
createUAS.addEventListener('click', ()=>{
  createUAC.style.display='none';
  reset.style.display='inline-block';
  createUAS.disabled=true;
  scenD.style.display='block';
  sceName.value='my_uas_scenario'
  sceName.insertAdjacentHTML("beforebegin","<span>uas_</spn>");
  sceType='uas';
})

// Start button script for initializing the xml file is in createUACxml.js

// INVITE
const uasFirst=document.getElementById('uasFirst');
const recvInviteB=document.getElementById('recv-invite-b');

// 1xx
const send1xxD=document.getElementById('send-1xx-d');
const send100B=document.getElementById('send-100-b');
const send180B=document.getElementById('send-180-b');
const send183B=document.getElementById('send-183-b');
// rel no-rel
const s100relD=document.getElementById('s-100rel-d');
const s100relB=document.getElementById('s-100-rel');
const sNo100relB=document.getElementById('s-no-100-rel');
// 1xx sdp
const s1xxSdpD=document.getElementById('s1xx-sdp-d');
const s1xxWoSdpB=document.getElementById('s1xx-wo-sdp-b');
const s1xxWsdpB=document.getElementById('s1xx-with-sdp-b');
const sPrackD=document.getElementById('s-prack-d');
const recvPrackB=document.getElementById('recv-prack-b');
const send200pB=document.getElementById('send-200p-b');
const send200pSdpB=document.getElementById('send-200p-sdp-b');
// 200 OK
const send200invSdpB=document.getElementById('send-200-inv-b');
const send200invB=document.getElementById('send-200-inv-no-sdp-b');
// ACK 
const recvAckB=document.getElementById('recv-ack');
// UAS new Requests
const uasRecvRqstD=document.getElementById('uas-recv-rqst');
const uasSendRqstD=document.getElementById('uas-send-request');
const uasRecvUpdateB=document.getElementById('uas-recv-update-b');
const uasSendInviteB=document.getElementById('uas-send-inv-b');
// BYE
const uasByeD=document.getElementById('uas-bye');
const uasRecvByeB=document.getElementById('uas-recv-bye');
const uasSendByeB=document.getElementById('uas-send-bye');


// Recv INVITE **************************************************************************

let invSeqRel=0, newInvSeq=0;

recvInviteB.addEventListener('click', () => {
  const recvInv = `
    <recv request="INVITE" crlf="true">
      <action>
        <!-- INV Placeholder to store vars -->
      </action>
    </recv>
    `;
  editor.setValue(`${editor.getValue()}\n${recvInv}`);
  newInvSeq++;
  recvInviteB.disabled=true;
  send1xxD.style.display='block';
  send200invB.style.display='inline-block';
  send200invSdpB.style.display='inline-block';
  start.disabled=true;
  send180B.disabled=false;
  send183B.disabled=false;
  send200invB.disabled=false;
  send200invSdpB.disabled=false;
  uasRecvUpdateB.disabled=true;
});


// Send 1xx ***************************************************************************
let s1xxCode=100;
let s1xxTxt='Trying';
let sRseq=0;
let s1xxRel=false;

send100B.addEventListener('click',()=>{
  s1xxCode=100;
  s1xxTxt='Trying';
  send100B.disabled=true;
  generateSend1xx(false);
});

send180B.addEventListener('click',()=>{
  s1xxCode=180;
  s1xxTxt='Ringing';
  send180B.disabled=true;
  send100B.disabled=true;
  s100relD.style.display='block';
  send183B.disabled=true;
  sNo100relB.disabled=false;
  sNo100relB.textContent='180 Not Reliable'
  s100relB.disabled=false;
  s100relB.textContent='180 Reliable'
  send200invB.disabled=true;
  send200invSdpB.disabled=true;
  s1xxSdpD.style.display='none';
});

send183B.addEventListener('click',()=>{
  s1xxCode=183;
  s1xxTxt='Session Progress';
  send183B.disabled=true;
  send100B.disabled=true;
  s100relD.style.display='block';
  send180B.disabled=true;
  sNo100relB.disabled=false;
  sNo100relB.textContent='183 Not Reliable'
  s100relB.disabled=false;
  s100relB.textContent='183 Reliable'
  s1xxSdpD.style.display='none';
  send200invB.disabled=true;
  send200invSdpB.disabled=true;
});

s100relB.addEventListener('click',()=>{
  invSeqRel=newInvSeq;
  s1xxRel=true;
  s100relD.style.display='none';
  s1xxSdpD.style.display='block';
  s1xxWoSdpB.disabled=false;
  s1xxWoSdpB.textContent=s1xxCode + ' without SDP';
  s1xxWsdpB.disabled=false;
  s1xxWsdpB.textContent=s1xxCode + ' with SDP';
});

sNo100relB.addEventListener('click',()=>{
  s1xxRel=false;
  s100relD.style.display='none';
  s1xxSdpD.style.display='block';
  sNo100relB.disabled=true;
  s100relB.disabled=true;
  s1xxWoSdpB.disabled=false;
  s1xxWoSdpB.textContent=s1xxCode + ' without SDP';
  s1xxWsdpB.disabled=false;
  s1xxWsdpB.textContent=s1xxCode + ' with SDP';
});

s1xxWoSdpB.addEventListener('click',()=>{
    if(s1xxRel===true){
      sRseq++;
      sPrackD.style.display='block';
      recvPrackB.style.display='inline-block';
      recvPrackB.disabled=false;
    };
    if(s1xxRel===false){
      send180B.disabled=false;
      send183B.disabled=false;
      send200invB.disabled=false;
      send200invSdpB.disabled=false;
    };
    generateSend1xx(s1xxRel,false);
    s1xxWoSdpB.disabled=true;
    s1xxWsdpB.disabled=true;
});
s1xxWsdpB.addEventListener('click',()=>{
    if(s1xxRel===true){
      sRseq++;
      sPrackD.style.display='block';
      recvPrackB.style.display='inline-block';
      recvPrackB.disabled=false;
    };
    if(s1xxRel===false){
      send180B.disabled=false;
      send183B.disabled=false;
      send200invB.disabled=false;
      send200invSdpB.disabled=false;
    };
    generateSend1xx(s1xxRel,true);
    s1xxWoSdpB.disabled=true;
    s1xxWsdpB.disabled=true;
});

// ********
let hVia='[last_Via:]';
let hCSeq='[last_CSeq:]';
let sdpBody=`
        v=0
        o=user1 53655765 2353687637 IN IP[local_ip_type] [local_ip]
        s=-
        c=IN IP[media_ip_type] [media_ip]
        t=0 0
        m=audio [media_port] RTP/AVP 0
        a=rtpmap:0 PCMU/8000`;

function generateSend1xx(srel,ssdp){
    if(sRseq>=1 && invSeqRel===newInvSeq){
        hVia='Via:[$' + invSeqRel + ']';
        hCSeq='CSeq:[$' + (50+invSeqRel) + ']';
    }
    else if (newInvSeq>invSeqRel){
      hVia='[last_Via:]';
      hCSeq='[last_CSeq:]';
    };

    if(invSeqRel===newInvSeq){
    var currentContent=editor.getValue();
    var originalXML=`<!-- INV Placeholder to store vars -->`;
    var replacementXML=`<ereg regexp=".*" search_in="hdr" header="Via:" check_it="true" assign_to="${invSeqRel}" />
        <ereg regexp=".*" search_in="hdr" header="CSeq:" check_it="true" assign_to="${50 + invSeqRel}" />
        <!-- INV Placeholder to store vars -->`;
      
    var lastIndex = currentContent.lastIndexOf(originalXML);

    if (lastIndex !== -1) {
      var modifiedContent = currentContent.substring(0, lastIndex) + replacementXML + currentContent.substring(lastIndex + originalXML.length);
    }

    // Set the modified content back to the editor
    editor.setValue(modifiedContent);
    };

    let sRequire=srel?`
        Require:100Rel
        RSeq:${sRseq}`:'';

    const sdp=ssdp
    ?`Content-Type: application/sdp
        Content-Length: [len]
        ${sdpBody}`
    : 'Content-Length: 0';

    const send1xx=`
    <send>
      <![CDATA[

        SIP/2.0 ${s1xxCode} ${s1xxTxt}
        ${hVia}
        [last_From:]
        [last_To:];tag=[pid]SIPpTag01[call_number]
        [last_Call-ID:]
        ${hCSeq} ${sRequire}
        Contact: <sip:[local_ip]:[local_port];transport=[transport]>
        ${sdp}

      ]]>
    </send>
  `;
  editor.setValue(`${editor.getValue()}\n${send1xx}`);
};

// Recv PRACK ***********************************************************************************
recvPrackB.addEventListener('click',()=>{
    const recvPrack=`
    <recv request="PRACK" crlf="true">
    </recv>`;
    editor.setValue(`${editor.getValue()}\n${recvPrack}`);
    recvPrackB.disabled=true;
    send200pB.style.display='inline-block';
    send200pSdpB.style.display='inline-block';
    send200pB.disabled=false;
    send200pSdpB.disabled=false;
});

// Send 200 for PRACK ******************************************************************************
send200pB.addEventListener('click',()=>{
    hVia='[last_Via:]';
    hCSeq='[last_CSeq:]';
    send200Ok(false);
    send200pB.disabled=true;
    send200pSdpB.disabled=true;
    send180B.disabled=false;
    send183B.disabled=false;
    send200invB.disabled=false;
    send200invSdpB.disabled=false;
});

send200pSdpB.addEventListener('click',()=>{
    hVia='[last_Via:]';
    hCSeq='[last_CSeq:]';
    send200Ok(true);
    send200pB.disabled=true;
    send200pSdpB.disabled=true;
    send180B.disabled=false;
    send183B.disabled=false;
    send200invB.disabled=false;
    send200invSdpB.disabled=false;
});

// Send 200 for invite ******************************************************************************
send200invSdpB.addEventListener('click',()=>{
  if(sRseq>=1 && invSeqRel===newInvSeq){
    hVia='Via:[$' + invSeqRel + ']';
    hCSeq='CSeq:[$' + (50+invSeqRel) + ']';
    }
    else if (newInvSeq>invSeqRel){
      hVia='[last_Via:]';
      hCSeq='[last_CSeq:]';
    };
    send200Ok(true);
    send200invB.disabled=true;
    send200invSdpB.disabled=true;
    send180B.disabled=true;
    send183B.disabled=true;
    recvAckB.style.display='block';
    recvAckB.disabled=false;
});
send200invB.addEventListener('click',()=>{
  if(sRseq>=1 && invSeqRel===newInvSeq){
    hVia='Via:[$' + invSeqRel + ']';
    hCSeq='CSeq:[$' + (50+invSeqRel) + ']';
    }
    else if (newInvSeq>invSeqRel){
      hVia='[last_Via:]';
      hCSeq='[last_CSeq:]';
    };
    send200Ok(false);
    send200invB.disabled=true;
    send200invSdpB.disabled=true;
    send180B.disabled=true;
    send183B.disabled=true;
    recvAckB.style.display='block';
});

/* 200 Ok generation for both PRACK and INVITE */
function send200Ok(sdp2){
    const sdp=sdp2
    ?`Content-Type: application/sdp
        Content-Length: [len]
        ${sdpBody}`
    : 'Content-Length: 0';

    const msg200=`
    <send>
      <![CDATA[
 
        SIP/2.0 200 OK
        ${hVia}
        [last_From:]
        [last_To:]
        [last_Call-ID:]
        ${hCSeq}
        [last_Record-Route:]
        Supported: timer,100rel
        Contact: <sip:[local_ip]:[local_port];transport=[transport]>
        ${sdp}
 
      ]]>
    </send>
    `;
    editor.setValue(`${editor.getValue()}\n${msg200}`);
};

// Recv ACK ****************************************************************************************
recvAckB.addEventListener('click',()=>{
  const recvAck=`
    <recv request="ACK" rtd="true" crlf="true">
    </recv>`;
   editor.setValue(`${editor.getValue()}\n${recvAck}`);
   recvAckB.disabled=true;
   recvInviteB.disabled=false;
   uasRecvRqstD.style.display='block';
   uasSendRqstD.style.display='block';
   uasRecvUpdateB.disabled=false;
   uasByeD.style.display='block';
});


// New Request from UAS
let uasCSeq=1;
function newRequestFromUas(){
  var currentContent=editor.getValue();
  var originalXML=`<!-- INV Placeholder to store vars -->`;
  var replacementXML=`<ereg regexp=".*" search_in="hdr" header="From:" check_it="true" assign_to="remote_from" />
        <ereg regexp=".*" search_in="hdr" header="To:" check_it="true" assign_to="remote_to" />
        <!-- INV Placeholder to store vars -->`;
    
  var firstIndex = currentContent.indexOf(originalXML);

  if (lastIndex !== -1) {
    var modifiedContent = currentContent.substring(0, firstIndex) + replacementXML + currentContent.substring(firstIndex + originalXML.length);
  }
  editor.setValue(modifiedContent);
};


// Recv BYE ****************************************************************************************
uasRecvByeB.addEventListener('click',()=>{
  const uasRecvBye=`
    <recv request="BYE">
    </recv>

    <send>
      <![CDATA[

        SIP/2.0 200 OK
        [last_Via:]
        [last_From:]
        [last_To:]
        [last_Call-ID:]
        [last_CSeq:]
        Contact: <sip:[local_ip]:[local_port];transport=[transport]>
        Content-Length: 0

      ]]>
    </send>

  <!-- definition of the response time repartition table (unit is ms)   -->
  <ResponseTimeRepartition value="10, 20, 30, 40, 50, 100, 150, 200"/>

  <!-- definition of the call length repartition table (unit is ms)     -->
  <CallLengthRepartition value="10, 50, 100, 500, 1000, 5000, 10000"/>

</scenario>
  `;
  editor.setValue(`${editor.getValue()}\n${uasRecvBye}`);
  recvInviteB.disabled=true;
  uasRecvByeB.disabled=true;
});




// Send BYE ********************************************************************************
uasSendByeB.addEventListener('click',()=>{
  console.log(uasCSeq);
  if (uasCSeq===1){newRequestFromUas();};
  uasCSeq++;
  const uasSendBye=`
    <send retrans="500">
      <![CDATA[

        BYE sip:[service]@[remote_ip]:[remote_port] SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: [$remote_to];tag=[pid]SIPpTag01[call_number]
        To: [$remote_from]
        Call-ID: [call_id]
        CSeq: ${uasCSeq} BYE
        Contact: sip:sipp@[local_ip]:[local_port]
        Max-Forwards: 70
        Subject: Performance Test
        Content-Length: 0

      ]]>
    </send>


    <recv response="200" crlf="true">
    </recv>


    <!-- definition of the response time repartition table (unit is ms)   -->
    <ResponseTimeRepartition value="10, 20, 30, 40, 50, 100, 150, 200"/>

    <!-- definition of the call length repartition table (unit is ms)     -->
    <CallLengthRepartition value="10, 50, 100, 500, 1000, 5000, 10000"/>

</scenario>
  `;
  editor.setValue(`${editor.getValue()}\n${uasSendBye}`);
  recvInviteB.disabled=true;
  uasRecvByeB.disabled=true;
});
