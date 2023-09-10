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

// Recv INVITE
recvInviteB.addEventListener('click', () => {
  const recvInv = `
    <recv request="INVITE" crlf="true">
    </recv>
    `;
  editor.setValue(`${editor.getValue()}\n${recvInv}`);
  recvInviteB.disabled=true;
  send1xxD.style.display='block';
  send200invB.style.display='inline-block';
  send200invSdpB.style.display='inline-block';
  start.disabled=true;
});


// Send 1xx *************************
let s1xxCode=100;
let s1xxTxt='Trying';
let sRseq=0

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
  s100relB.disabled=false;
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
  s100relB.disabled=false;
  s1xxSdpD.style.display='none';
});

s100relB.addEventListener('click',()=>{
  s100relD.style.display='none';
  s1xxSdpD.style.display='block';
  s1xxWoSdpB.disabled=false;
  s1xxWsdpB.disabled=false;
});

sNo100relB.addEventListener('click',()=>{
  generateSend1xx(false,false);
  sNo100relB.disabled=true;
  s100relB.disabled=true;
  send180B.disabled=false;
  send183B.disabled=false;
});

s1xxWoSdpB.addEventListener('click',()=>{
    sRseq++;
    generateSend1xx(true,false);
    s1xxWoSdpB.disabled=true;
    s1xxWsdpB.disabled=true;
    sPrackD.style.display='block';
    recvPrackB.style.display='inline-block';
    recvPrackB.disabled=false;
});
s1xxWsdpB.addEventListener('click',()=>{
    sRseq++;
    generateSend1xx(true,true);
    s1xxWoSdpB.disabled=true;
    s1xxWsdpB.disabled=true;
    sPrackD.style.display='block';
    recvPrackB.style.display='inline-block';
    recvPrackB.disabled=false;
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
    if(sRseq>=1){
        hVia='Via:[$1]';
        hCSeq='CSeq:[$2]';
    }

    if(sRseq===1){
    var currentContent=editor.getValue();
    var originalXML=`<recv request="INVITE" crlf="true">`;
    var replacementXML=`
    <recv request="INVITE" crlf="true" rrs="true">
      <action>
        <ereg regexp=".*" search_in="hdr" header="Via:" check_it="true" assign_to="1" />
        <ereg regexp=".*" search_in="hdr" header="CSeq:" check_it="true" assign_to="2" />
      </action>`;
        
    var modifiedContent=currentContent.replace(originalXML, replacementXML);
    
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

// Recv PRACK
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

// Send 200 for PRACK 
send200pB.addEventListener('click',()=>{
    hVia='[last_Via:]';
    hCSeq='[last_CSeq:]';
    send200Ok(false);
    send200pB.disabled=true;
    send200pSdpB.disabled=true;
    send180B.disabled=false;
    send183B.disabled=false;
});

send200pSdpB.addEventListener('click',()=>{
    hVia='[last_Via:]';
    hCSeq='[last_CSeq:]';
    send200Ok(true);
    send200pB.disabled=true;
    send200pSdpB.disabled=true;
    send180B.disabled=false;
    send183B.disabled=false;
});

send200invSdpB.addEventListener('click',()=>{
    if(sRseq>=1){
        hVia='Via:[$1]';
        hCSeq='CSeq:[$2]';
    }
    send200Ok(true);
    send200invB.disabled=true;
    send200invSdpB.disabled=true;
    send180B.disabled=true;
    send183B.disabled=true;
});
send200invB.addEventListener('click',()=>{
    if(sRseq>=1){
        hVia='Via:[$1]';
        hCSeq='CSeq:[$2]';
    }
    send200Ok(false);
    send200invB.disabled=true;
    send200invSdpB.disabled=true;
    send180B.disabled=true;
    send183B.disabled=true;
});

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