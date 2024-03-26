# kSipP - for Everyone!

SipP is a powerful tool for VoIP testing in the telecom world, but it often requires command-line expertise. 
kSipP aims to bridge this gap by providing a user-friendly graphical user interface (GUI) built with Django and Python.

## Features:
- Simplified Configuration: Easily create and edit SipP scenarios without needing to write complex command-line arguments.
- Intuitive Interface: A well-designed GUI streamlines the process of defining SIP messages, call flows, and test parameters.
- Effortless Execution: Launch your SipP tests with a click – no more manual command-line manipulation.
- Visualized Results: Gain insights into test outcomes through clear and concise visualizations.

## Who's it for?

- VoIP Testers: Save time and effort with a streamlined SipP testing experience.
- Network Engineers: Quickly validate SIP functionality without extensive command-line knowledge.
- Developers: Easily integrate SipP testing into their development workflows.

## How to use?

If you run it with docker, its pretty easy too!
https://hub.docker.com/r/krndwr/ksipp
```
docker run -dt --network host --name ksipp krndwr/ksipp
```
Once your container is up and running, open it http://localhost:8080/ (or whatever your linux/docker IP:8080)

We welcome contributions from the community! Feel free to fork the repository, propose bug fixes, or add new features through pull requests.

![kSipP - Easy SipP GUI for Everyone](https://raw.githubusercontent.com/kiran-daware/kSipP/main/screenshot.png)

### Disclaimer: 
This project is still work in progress and is uploaded on git hub as is without any warranty of any kind. The project has included the sipp binary from https://github.com/SIPp/sipp which is licenced under GNU General Public License.
