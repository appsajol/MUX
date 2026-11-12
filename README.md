MUX V2.6 – Cyber Neon

A Firebase-powered terminal chat application for Termux.

MUX is a Python-based terminal application with a cyber-themed interface, Firebase Authentication, Realtime Database messaging, online presence, and local chat history.

Features

- Cyber Neon terminal interface
- Firebase Email/Password Authentication
- Realtime group chat
- Online member list
- User presence and heartbeat
- Local chat history using SQLite
- Multiple terminal themes
- Header customization
- Simple installer

Requirements

- Android device
- "Termux" (https://github.com/termux/termux-app)
- Internet connection
- Python 3
- A configured Firebase project

Installation

Open Termux and run these commands:
```
pkg update -y
pkg install git python python-pip -y
git clone https://github.com/appsajol/mux.git
cd mux
bash install.sh
```
After installation, launch MUX:
```
mux
```
Update MUX

To get the latest version from GitHub:
```
cd ~/mux
git pull origin main
bash install.sh
```
Then restart MUX:
```
mux
```
Uninstall MUX
To remove the MUX launcher:
```
rm -f ~/.local/bin/mux
```
To also remove the downloaded source folder:
```
rm -rf ~/mux
```
Optional: Delete your local MUX data
This permanently removes local configuration and SQLite chat history:
```
rm -rf ~/.mux
```
Do not run the optional command if you want to keep your local data.

Chat Commands

Command| Description
"/members"| Show online members
"/history"| View chat history
"/clear"| Clear local chat history
"/help"| Show available commands
"/exit"| Exit the chat

Firebase Setup

MUX requires a Firebase project configured with:

1. Email/Password Authentication enabled.
2. Realtime Database created.
3. The correct Firebase configuration added to the application.
4. Appropriate database security rules.

Security notice: Do not use unrestricted database read/write rules in a public deployment. Configure authentication, group membership authorization, and message validation before allowing public use.

Never publish Firebase service-account private keys or other administrator credentials.

Project Information

- Project: MUX
- Version: 2.6
- Theme: Cyber Neon
- Platform: Termux / Android
- Language: Python
- Backend: Firebase Realtime Database

Developer

GitHub: https://github.com/appsajol

License
Choose and add an appropriate open-source license before distributing this project.
