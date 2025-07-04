# easySIPp - SIP Testing, Simplified.

> **🚨 Project Renamed:** This project was formerly known as `kSipP`. It is now called **easySIPp** to better reflect its mission of making SIP testing simpler and more accessible. All functionality remains the same. Please update your bookmarks or references to the new name:  
> **New URL:** https://github.com/kiran-daware/easySIPp  
> *(Old links will still redirect properly.)*

---

## 🚀 What is easySIPp?

[SIPp](https://github.com/SIPp/sipp) is a powerful CLI-based tool used in the telecom world for **VoIP SIP testing**, but it requires command-line expertise. That steep learning curve can be a barrier for many.

**easySIPp** is a **web-based graphical user interface (GUI)** that runs on top of SIPp, enabling users to run, manage, and visualize SIP tests effortlessly — no command-line skills required.

---

## ✨ Features

- **Effortless Scenario Creation**  
  Build and edit complex **SIPp XML scenarios** directly in the browser — no need to write raw XML.  
  👉 Try the [Online SIPp XML Generator](https://kiran-daware.github.io/sipp-xml/)

- **Intuitive Test Configuration**  
  Configure call flows, caller/callee numbers, rates, number of calls, and more through a simple Web GUI.

- **One-Click Execution**  
  Run SIPp scenarios instantly — no scripts or terminal needed.

- **Live Output Streaming**  
  Watch SIPp results and logs in real time, just like you would in the terminal.

- **Seamless SIPp Integration**  
  Under the hood, it’s still the real SIPp — just with a modern frontend.

---

## 🤖 Who Should Use This?

- **VoIP Testers & QA Engineers**  
  Streamline your testing workflow with an intuitive UI.

- **Telecom Devs & Network Engineers**  
  Focus on your SIP logic, not scripting.

- **Anyone wanting an easier SIPp experience**  
  Whether you're new or experienced, easySIPp makes SIP testing easier for everyone.

---

## 🐳 How to Use (with Docker)

Get up and running in seconds using Docker:

[![](https://img.shields.io/docker/pulls/krndwr/ksipp)](https://hub.docker.com/r/krndwr/ksipp)

```bash
docker run -dt --network host --name ksipp krndwr/ksipp
```
Once your container is up and running, open your browser and go to http://localhost:8080/ (or <your_linux/docker_IP>:8080)

---

## ❓ Frequently Asked Questions

### 🔹 What is easySIPp?
A web-based frontend for [SIPp](https://github.com/SIPp/sipp), making SIP call testing accessible via a modern interface.

### 🔹 Does it replace SIPp?
No — it enhances it. It still runs the original SIPp engine under the hood.

### 🔹 Is it open source?
Yes! Contributions are welcome. Fork the repo, create issues, or open pull requests.

### 🔹 Can I still use the old repo (`kSipP`)?
Old links will redirect, but please use the new name (`easySIPp`) moving forward for clarity and consistency.

---

## ⚠️ Disclaimer

This project is a work in progress and is provided **"as is"** without any warranty. It bundles the [SIPp](https://github.com/SIPp/sipp) binary, which is licensed under the **GNU General Public License (GPL)**. You're responsible for complying with the license terms.

## 📸 Screenshots

### Main Dashboard & Test Execution
![easySIPp - Web GUI for SIPp](https://raw.githubusercontent.com/kiran-daware/easySIPp/main/screenshot-1.png)

### Realtime status check control of running SIPp calls
![easySIPp - SIPp control and real-time status](https://raw.githubusercontent.com/kiran-daware/easySIPp/main/screenshot-4.png)

### SIP Call Flow Visualization
![easySIPp - XML flow diagram](https://raw.githubusercontent.com/kiran-daware/easySIPp/main/screenshot-2.png)

### SIPp XML Scenario Generator
![easySIPp - XML Scenario generator](https://raw.githubusercontent.com/kiran-daware/easySIPp/main/screenshot-3.png)
