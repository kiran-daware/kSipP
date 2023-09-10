var editor = ace.edit("xml-editor");
editor.session.setMode("ace/mode/xml");
editor.setTheme("ace/theme/chrome");
editor.setFontSize('13px');
// Scroll to the bottom line
editor.session.on('change', () => {
    editor.renderer.scrollToLine(Number.POSITIVE_INFINITY)
})
// Select UAC/UAS/Reset
const createUAC=document.getElementById('createUAC');
const createUAS=document.getElementById('createUAS');
const reset=document.getElementById('reset');
const uacFirst=document.getElementById('uacFirst');
const scenD=document.getElementById('scen-d');
const sceName=document.getElementById('scenario-name');
const start=document.getElementById('start');
// INVITE
const sendInviteB=document.getElementById('send-invite');
const sendInviteD=document.getElementById('send-invite-div');
const inviteWithSdpB=document.getElementById('invite-with-sdp');
const inviteWithoutSdpB=document.getElementById('invite-without-sdp');
// 1xx
const receive1xxD=document.getElementById('recv-1xx');
const receive100B=document.getElementById('recv-100');
const receive180B=document.getElementById('recv-180');
const receive183B=document.getElementById('recv-183');
// Rel / Norel
const reliableD=document.getElementById('100rel-d');
const relB=document.getElementById('100-rel');
const noRelB=document.getElementById('no-100-rel');
const prackD=document.getElementById('prack-d');
const pWithSdp=document.getElementById('p-with-sdp-b');
const pWoSdp=document.getElementById('p-wo-sdp-b');
const recv200PrackB=document.getElementById('recv-200prack-b');
// 2xx
const recv2xxD=document.getElementById('recv-2xx');
const recv200B=document.getElementById('recv-200');
// recv failiure cause code
const recvFailCodeD=document.getElementById('recv-failcode');
const recvFxxB=document.getElementById('recv-fxx');
const recvCauseD=document.getElementById('recv-cause');
const recvCodeI=document.getElementById('r-cause-code');
const sendFailAck=document.getElementById('fail-ack')
// ACK
const sendAckD=document.getElementById('send-ack-div');
const sendAckB=document.getElementById('send-ack');
const sendAckSdpB=document.getElementById('send-ack-sdp');
// Play Media / Pause
const playMediaB=document.getElementById('play-media-b');
const pauseD=document.getElementById('pause-d');
const pauseB=document.getElementById('pause-b');
const pauseMsI=document.getElementById('pause-ms');
// mid dialogue requests
const midDiaReqD=document.getElementById('mid-dia-req');
const reInvB=document.getElementById('reinv-b');
const updateB=document.getElementById('update-b');
const referB=document.getElementById('refer-b');
const midDiaSdpD=document.getElementById('mid-dia-sdp-div');
const midWsdp=document.getElementById('mid-with-sdp');
const midWoSdp=document.getElementById('mid-without-sdp');
const midRecv200B=document.getElementById('mid-req-200-b');
// BYE
const sendrecvByeD=document.getElementById('sendrecv-bye');
const sendByeB=document.getElementById('send-bye');
const recvByeB=document.getElementById('recv-bye');

let cseq=1;
let invcseq=1
let sceType='uac'
let method='INVITE'

createUAC.addEventListener('click', () => {
    createUAS.style.display='none';
    createUAC.disabled=true;
    reset.style.display='inline-block';
    scenD.style.display='block';
    sceName.value='my_uac_scenario'
    sceName.insertAdjacentHTML("beforebegin","<span>uac_</spn>");
    sceType='uac';
})

reset.addEventListener('click', ()=>{
    location.reload();
})

// Editor xml header for sip
start.addEventListener('click',()=>{
  const scenHeader=`<?xml version="1.0" encoding="ISO-8859-1" ?>
<!DOCTYPE scenario SYSTEM "sipp.dtd">

<!-- This program is distributed in the hope that it will be useful,    -->
<!-- but WITHOUT ANY WARRANTY; without even the implied warranty of     -->
<!-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the      -->
<!-- GNU General Public License for more details.                       -->

<!-- This scenario is created by kSipP scenario Creator                 -->

<scenario name="${sceType}_${sceName.value}">
  `;
  editor.setValue(scenHeader);
  if(sceType==='uac'){
    uacFirst.style.display='block';
  }else if (sceType==='uas'){
    uasFirst.style.display='block';
  };

});

// Send INVITE *************************

sendInviteB.addEventListener('click', () => {
sendInviteD.style.display='block';
sendInviteB.disabled=true;
inviteWithSdpB.disabled=false;
inviteWithoutSdpB.disabled=false;
sendInviteB.style.display='none';
});


inviteWithSdpB.addEventListener('click', () => {
    method='INVITE';
    generateRequest(true);
    sendInviteB.style.display='block';
    sendInviteD.style.display='none';
    recvFailCodeD.style.display='block';
});

inviteWithoutSdpB.addEventListener('click', () => {
    method='INVITE';
    generateRequest(false);
    sendInviteB.style.display='block';
    sendInviteD.style.display='none';
    recvFailCodeD.style.display='block';
});

function generateRequest(includeSDP) {
    const sdp=includeSDP 
    ?`Content-Type: application/sdp
        Content-Length: [len]

        v=0
        o=user1 53655765 2353687637 IN IP[local_ip_type] [local_ip]
        s=-
        c=IN IP[media_ip_type] [media_ip]
        t=0 0
        m=audio [media_port] RTP/AVP 0
        a=rtpmap:0 PCMU/8000`
    : 'Content-Length: 0';

    const reqMessage=`
    <send retrans="500">
      <![CDATA[

        ${method} sip:[service]@[remote_ip]:[remote_port] SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: sipp <sip:sipp@[local_ip]:[local_port]>;tag=[pid]SIPpTag00[call_number]
        To: sut <sip:[service]@[remote_ip]:[remote_port]>
        Call-ID: [call_id]
        CSeq: ${cseq} ${method}
        Contact: sip:sipp@[local_ip]:[local_port]
        Max-Forwards: 70
        Subject: Performance Test
        ${sdp}

      ]]>
    </send>
    `;
  invcseq=cseq;
  cseq++;
  editor.setValue(`${editor.getValue()}\n${reqMessage}`);
  receive1xxD.style.display='block';
  sceName.disabled=true;
  start.disabled=true;
  if(method==='INVITE'){
  receive100B.disabled=false;
  receive180B.disabled=false;
  receive183B.disabled=false;
  recv2xxD.style.display='block';
  recv200B.disabled=false;
  }else{};
};


// Recv 1xx *************************
receive100B.addEventListener('click', () => {
const response100 = `
    <recv response="100" optional="true">
    </recv>
    `;
editor.setValue(`${editor.getValue()}\n${response100}`);
receive100B.disabled=true;
});

let oxx=180;
let fromto=true;
let rseq=11;

receive180B.addEventListener('click', () => {
  reliableD.style.display='block';
  prackD.style.display='none';
  oxx=180;
  receive100B.disabled=true;
  receive180B.disabled=true;
  receive183B.disabled=true;
  recv200B.disabled=true;
  relB.disabled=false;
  noRelB.disabled=false;
  recvFailCodeD.style.display='none';
  });

receive183B.addEventListener('click', () => {
  reliableD.style.display='block';
  prackD.style.display='none';
  oxx=183;
  receive100B.disabled=true;
  receive180B.disabled=true;
  receive183B.disabled=true;
  recv200B.disabled=true;
  relB.disabled=false;
  noRelB.disabled=false;
  recvFailCodeD.style.display='none';
  });

relB.addEventListener('click', () => {
  generate18x(true);
  reliableD.style.display='none';
  prackD.style.display='inline-block';
});

noRelB.addEventListener('click', () => {
  generate18x(false);
  relB.disabled=true;
  noRelB.disabled=true;
});

function generate18x(rel){
  let opt=rel?'':'optional="true"';
  const ft=fromto?`
        <ereg regexp=".*" search_in="hdr" header="From:" check_it="true" assign_to="1" />
        <ereg regexp=".*" search_in="hdr" header="To:" check_it="true" assign_to="2" />`
  :'';
  const rel18x=rel
  ?`
      <action>
        <ereg regexp=".*" search_in="hdr" header="RSeq:" check_it="true" assign_to="${rseq}" />${ft}
      </action>`
  :'';
  const response18x=`
    <recv response="${oxx}" ${opt}>${rel18x}
    </recv>
  `;
  editor.setValue(`${editor.getValue()}\n${response18x}`);
  if(rel){
    fromto=false;
    prackD.style.display='block';
    pWithSdp.disabled=false;
    pWoSdp.disabled=false;
  }else{
    receive180B.disabled=false;
    receive183B.disabled=false;
    recv200B.disabled=false;
  };
};


// PRACK *************************
pWithSdp.addEventListener('click',()=>{
  sendPrack(true);
  pWithSdp.disabled=true;
  pWoSdp.disabled=true;
});
pWoSdp.addEventListener('click',()=>{
  sendPrack(false);
  pWithSdp.disabled=true;
  pWoSdp.disabled=true;
});

function sendPrack(wosdp){
  const sdp=wosdp 
    ?`Content-Type: application/sdp
        Content-Length: [len]

        v=0
        o=user1 53655765 2353687639 IN IP[local_ip_type] [local_ip]
        s=-
        c=IN IP[media_ip_type] [media_ip]
        t=0 0
        m=audio [media_port] RTP/AVP 0
        a=rtpmap:0 PCMU/8000`
    : 'Content-Length: 0';

  const sendPrack=`
    <send retrans="1500">
      <![CDATA[

        PRACK sip:[service]@[remote_ip]:[remote_port] SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: [$1]
        To: [$2]
        Call-ID: [call_id]
        CSeq: ${cseq} PRACK
        Contact: sip:sipp@[local_ip]:[local_port]
        Max-Forwards: 70
        RAck: [$${rseq}] ${invcseq} INVITE
        ${sdp}

      ]]>
    </send>
  `;
  editor.setValue(`${editor.getValue()}\n${sendPrack}`);
  receive100B.disabled=true;
  recv200PrackB.disabled=false;
  recv200PrackB.style.display='inline-block';
  cseq++;
  rseq++;
};


recv200PrackB.addEventListener('click', ()=>{
  const recv200P=`
    <recv response="200" rtd="true">
    </recv>
  `;
  editor.setValue(`${editor.getValue()}\n${recv200P}`);
  receive180B.disabled=false;
  receive183B.disabled=false;
  recv200B.disabled=false;
  recv200PrackB.disabled=true;
  playMediaB.style.display='inline-block';
  playMediaB.disabled=false;
});


// Recv 2xx *************************
recv200B.addEventListener('click', () => {
const response200 =`
    <recv response="200" rtd="true">
    </recv>
    `;
editor.setValue(`${editor.getValue()}\n${response200}`);
receive100B.disabled=true;
receive180B.disabled=true;
receive183B.disabled=true;
recv200B.disabled=true;
sendAckD.style.display='block';
sendAckB.disabled=false;
sendAckSdpB.disabled=false;
playMediaB.disabled=true;
recvFailCodeD.style.display='none';
});

// Recv Failure Cause Code
recvFxxB.addEventListener('click',()=>{
  recvCauseD.style.display='block';
  receive100B.disabled=true;
  receive180B.disabled=true;
  receive183B.disabled=true;
  recv200B.disabled=true;
  recvFxxB.disabled=true;
});

sendFailAck.addEventListener('click',()=>{
  const cc=recvCodeI.value;
  const responseFxx=`
    <recv response="${cc}" rtd="true">
    </recv>
    `;
  editor.setValue(`${editor.getValue()}\n${responseFxx}`);
  sendAck(false);
  const footer=`
    <!-- definition of the response time repartition table (unit is ms)   -->
    <ResponseTimeRepartition value="10, 20, 30, 40, 50, 100, 150, 200"/>

    <!-- definition of the call length repartition table (unit is ms)     -->
    <CallLengthRepartition value="10, 50, 100, 500, 1000, 5000, 10000"/>

</scenario>
`;
  editor.setValue(`${editor.getValue()}\n${footer}`);
  sendFailAck.disabled=true;
  recvCodeI.disabled=true;
});


// Send ACK *************************
function sendAck(wosdp){
const sdp=wosdp 
    ?`Content-Type: application/sdp
        Content-Length: [len]

        v=0
        o=user1 53655765 2353687639 IN IP[local_ip_type] [local_ip]
        s=-
        c=IN IP[media_ip_type] [media_ip]
        t=0 0
        m=audio [media_port] RTP/AVP 0
        a=rtpmap:0 PCMU/8000`
    : 'Content-Length: 0';
const sendAck = `
    <send>
      <![CDATA[

        ACK sip:[service]@[remote_ip]:[remote_port] SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: sipp <sip:sipp@[local_ip]:[local_port]>;tag=[pid]SIPpTag00[call_number]
        To: sut <sip:[service]@[remote_ip]:[remote_port]>[peer_tag_param]
        Call-ID: [call_id]
        CSeq: ${invcseq} ACK
        Contact: sip:sipp@[local_ip]:[local_port]
        Max-Forwards: 70
        Subject: Performance Test
        ${sdp}

      ]]>
    </send>
`;
editor.setValue(`${editor.getValue()}\n${sendAck}`);}

function disableButtsForAck(){
  sendAckB.disabled=true;
  sendAckSdpB.disabled=true;
  sendrecvByeD.style.display='block';
  playMediaB.style.display='inline-block';
  playMediaB.disabled=false;
  invcseq++;
  midDiaReqD.style.display='block';
  reInvB.disabled=false;
  updateB.disabled=false;
  referB.disabled=false;
  pauseD.style.display='inline-block';
  pauseB.disabled=false;
  sendByeB.disabled=false;
  recvByeB.disabled=false;
  reInvB.disabled=false;
  updateB.disabled=false;
  referB.disabled=false;
};
sendAckB.addEventListener('click', () => {
  sendAck(false);
  disableButtsForAck();
});
sendAckSdpB.addEventListener('click', () => {
  sendAck(true);
  disableButtsForAck();
});

// Play Media *************************
playMediaB.addEventListener('click',()=>{
  const playMedia=`
    <!--  you may modify the path to your .pcap media file here -->
    <nop>
      <action>
        <exec play_pcap_audio="pcap/g711a.pcap"/>
      </action>
    </nop>
  `;
  editor.setValue(`${editor.getValue()}\n${playMedia}`);
  playMediaB.disabled=true;
});

// Pause Milliseconds *************************
pauseB.addEventListener('click',()=>{
  let misec=document.getElementById('pause-ms').value
  const pausems=`
    <pause milliseconds="${misec}"/>
    `;
  editor.setValue(`${editor.getValue()}\n${pausems}`);
  pauseB.disabled=true;
  pauseMsI.disabled=true;
});

// mid dialogue requests
// re-INVITE
reInvB.addEventListener('click',()=>{
  midDiaReqD.style.display='none';
  midDiaSdpD.style.display='block';
  reInvB.disabled=true;
  updateB.disabled=true;
  referB.disabled=true;
  method='INVITE';
  pauseB.disabled=true;
  pauseMsI.disabled=true;
  playMediaB.disabled=true;
  sendByeB.disabled=true;
  recvByeB.disabled=true;
  reInvB.disabled=true;
  updateB.disabled=true;
  referB.disabled=true;
});
// mid-dialogue UPDATE
updateB.addEventListener('click',()=>{
  midDiaReqD.style.display='none';
  midDiaSdpD.style.display='block';
  method='UPDATE';
  pauseB.disabled=true;
  pauseMsI.disabled=true;
  playMediaB.disabled=true;
  sendByeB.disabled=true;
  recvByeB.disabled=true;
  reInvB.disabled=true;
  updateB.disabled=true;
  referB.disabled=true;
});

midWsdp.addEventListener('click',()=>{
  generateRequest(true);
  midDiaReqD.style.display='block';
  midDiaSdpD.style.display='none';
  if(method!='INVITE'){midRecv200B.style.display='block';
    midRecv200B.disabled=false;};
});

midWoSdp.addEventListener('click',()=>{
  generateRequest(false);
  midDiaReqD.style.display='block';
  midDiaSdpD.style.display='none';
  if(method!='INVITE'){midRecv200B.style.display='block';
    midRecv200B.disabled=false;};
});

midRecv200B.addEventListener('click', () => {
  const response200 =`
    <recv response="200" rtd="true">
    </recv>
    `;
  editor.setValue(`${editor.getValue()}\n${response200}`);
  pauseB.disabled=false;
  pauseMsI.disabled=false;
  playMediaB.disabled=false;
  sendByeB.disabled=false;
  recvByeB.disabled=false;
  reInvB.disabled=false;
  updateB.disabled=false;
  referB.disabled=false;
  midRecv200B.disabled=true;
});


// Send BYE *************************
sendByeB.addEventListener('click',()=>{
const sendBye=`
    <send retrans="500">
      <![CDATA[

        BYE sip:[service]@[remote_ip]:[remote_port] SIP/2.0
        Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
        From: sipp <sip:sipp@[local_ip]:[local_port]>;tag=[pid]SIPpTag00[call_number]
        To: sut <sip:[service]@[remote_ip]:[remote_port]>[peer_tag_param]
        Call-ID: [call_id]
        CSeq: ${cseq} BYE
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
editor.setValue(`${editor.getValue()}\n${sendBye}`);
sendByeB.disabled=true;
recvByeB.disabled=true;
sendInviteB.disabled=true;
reInvB.disabled=true;
updateB.disabled=true;
referB.disabled=true;
playMediaB.disabled=true;
pauseB.disabled=true;
pauseMsI.disabled=true;
});


// Recv BYE *************************
recvByeB.addEventListener('click',()=>{
const recvBye=`
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
editor.setValue(`${editor.getValue()}\n${recvBye}`);
sendByeB.disabled=true;
recvByeB.disabled=true;
sendInviteB.disabled=true;
reInvB.disabled=true;
updateB.disabled=true;
referB.disabled=true;
playMediaB.disabled=true;
pauseB.disabled=true;
pauseMsI.disabled=true;
});

