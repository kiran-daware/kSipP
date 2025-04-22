# kSipP - for Everyone!

[SIPp](https://github.com/SIPp/sipp) is a powerful tool for **VoIP SIP testing** in the telecom world, but it often requires command-line expertise. It can be daunting for those unfamiliar with CLI tools. 
kSipP provides a user-friendly graphical user interface (**Web GUI**) for running **SIPp**.

## Features:
- Simplified Configuration: Easily create and edit **SIPp xml scenarios** without needing to write complex xml manually.
- Need to create SIPp XML scenarios without the full setup? Check out our online SIPp scenario builder hosted on GitHub Pages: [SIPp xml generator](https://kiran-daware.github.io/sipp-xml/)
- Intuitive Interface: A well-designed Web GUI streamlines the process of defining SIP messages, call flows, and test parameters.
- Effortless Execution: Launch your SIPp test calls with a click – no more manual command-line manipulation.
- Visualized Results: Gain insights into test outcomes through clear and concise visualizations.

## Who's it for?

- VoIP Testers: Save time and effort with a streamlined SIPp testing experience.
- Network Engineers: Quickly validate SIP functionality without extensive command-line knowledge.

## How to use?

Get up and running in seconds using Docker: 
https://hub.docker.com/r/krndwr/ksipp 
![Docker Pulls](https://img.shields.io/docker/pulls/krndwr/ksipp)

```
docker run -dt --network host --name ksipp krndwr/ksipp
```
Once your container is up and running, open it http://localhost:8080/ (or <your_linux/docker_IP>:8080)


![kSipP - Web GUI for SIPp](https://raw.githubusercontent.com/kiran-daware/kSipP/main/screenshot.png)


## ❓ Frequently Asked Questions

### What is kSipP?
kSipP is a **web-based GUI for [SIPp](https://github.com/SIPp/sipp)**, designed to simplify SIP and VoIP testing. It eliminates the need for complex command-line configurations and provides a more accessible interface for VOIP SIP testers.

### Who should use kSipP?
Anyone involved in SIP testing — including VoIP testers, telecom engineers — will benefit from kSipP's user-friendly approach to running and managing SIPp scenarios.

### Does kSipP replace the SIPp command-line tool?
kSipP doesn’t replace SipP — it enhances it. Under the hood, kSipP uses the original SIPp engine, but gives you a GUI to interact with it more easily.

### Is kSipP open-source?
Yes! kSipP is an open-source project. We welcome contributions from the community! Feel free to fork the repository, propose bug fixes, or add new features through pull requests.

### How do I run kSipP using Docker?
Just run the following command:
```bash
docker run -dt --network host --name ksipp krndwr/ksipp
```


### Disclaimer: 
This project is a work in progress and is uploaded on git hub as is without any warranty of any kind. The project has included the sipp binary from https://github.com/SIPp/sipp which is licenced under GNU General Public License.
