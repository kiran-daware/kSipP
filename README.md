# easySIPp - Simplify Your SIP Testing. For Everyone.

[SIPp](https://github.com/SIPp/sipp) is a powerful tool for **VoIP SIP testing** in the telecom world, but it often requires command-line expertise. It can be daunting for those unfamiliar with CLI tools. 
easySIPp provides a user-friendly graphical user interface (**Web GUI**) that simplifies the entire process of running and managing **SIPp**. Thus, making advanced SIP testing accessible to **everyone**.

## Features:
* **Effortless Scenario Creation:** Generate and modify complex **SIPp XML scenarios** directly within your browser, eliminating the need for complex XML coding manually.
    * *Need to create SIPp XML scenarios without the full setup?* Check out our **online SIPp scenario builder**: [SIPp XML Generator](https://kiran-daware.github.io/sipp-xml/)
* **Intuitive Test Configuration:** A well-designed Web GUI streamlines the process of defining call flows, and crucial test parameters (like calling party and called party numbers, call rates and concurrent calls etc).
* **One-Click Execution:** (One-click if you have it pre-configured) Launch your SIPp test calls with a single click – no more tedious command-line manipulation or complex script.
* **SIPp refreshing Results:** View the results of SIPp processes as they are running just like you could see in your CLI.
* **Seamless SIPp Integration:** easySIPp enhances SIPp's usability without sacrificing its core power, running the original SIPp engine under the hood.

## Who's it for?

* **VoIP Testers:** Streamline your SIPp testing workflow and save valuable time.
* **Anyone looking to simplify their SIP testing experience!**

## How to use?

Get up and running in seconds using Docker: 
https://hub.docker.com/r/krndwr/ksipp 
![Docker Pulls](https://img.shields.io/docker/pulls/krndwr/ksipp)

```
docker run -dt --network host --name ksipp krndwr/ksipp
```
Once your container is up and running, open it http://localhost:8080/ (or <your_linux/docker_IP>:8080)

## ❓ Frequently Asked Questions

### What is easySIPp?
easySIPp is a **web-based GUI for [SIPp](https://github.com/SIPp/sipp)**, designed to simplify SIP and VoIP testing. Its primary goal is to simplify complex SIP and VoIP testing by providing an accessible and intuitive platform, eliminating the need for extensive command-line expertise.

### Who should use easySIPp?
Anyone involved in SIP testing — including VoIP testers, telecom engineers — will benefit from easySIPp's user-friendly approach to running and managing SIPp scenarios.

### Does easySIPp replace the SIPp command-line tool?
easySIPp doesn’t replace SipP — it enhances it. Under the hood, easySIPp uses the original SIPp engine, but gives you a GUI to interact with it more easily.

### Is easySIPp open-source?
Yes! easySIPp is an open-source project. We welcome contributions from the community! Feel free to fork the repository, propose bug fixes, or add new features through pull requests.

### How do I run easySIPp using Docker?
Just run the following command:
```bash
docker run -dt --network host --name ksipp krndwr/ksipp
```

### Disclaimer: 
This project is a work in progress and is provided "as is" without any warranty, express or implied, of any kind. The project includes the SIPp binary from https://github.com/SIPp/sipp, which is licensed under the GNU General Public License (GPL). Users are responsible for complying with the SIPp license.


## 📸 Screenshots

### Main Dashboard & Test Execution
![easySIPp - Web GUI for SIPp](https://raw.githubusercontent.com/kiran-daware/easySIPp/main/screenshot-1.png)

### SIP Call Flow Visualization
![easySIPp - XML flow diagram](https://raw.githubusercontent.com/kiran-daware/easySIPp/main/screenshot-2.png)

### SIPp XML Scenario Generator
![easySIPp - XML Scenario generator](https://raw.githubusercontent.com/kiran-daware/easySIPp/main/screenshot-3.png)