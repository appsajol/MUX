MUX Chat (mChat) V2.6 – Cyber Neon

A lightweight, Firebase-powered global group chat application built with Python for Termux on Android.

✨ Features

- 🌐 Global Group Chat
- 🔐 Firebase Email & Password Authentication
- 📝 Create a New Account
- 👤 User Profile
- 🟢 Online / Offline Presence
- 👥 Online Members List
- 💬 Real-time Message Updates
- 💾 Local SQLite Chat History
- ⚙️ Settings Menu
- ℹ️ About mChat
- 🎨 Cyber Neon Terminal Interface
- 📱 Designed for Android Termux

📋 Requirements

- Android device
- Termux
- Internet connection

🚀 Installation

Step 1: Update Termux
```
pkg update && pkg upgrade -y
```
Step 2: Install Git
```
pkg install git -y
```
Step 3: Clone the Repository
```
git clone https://github.com/appsajol/mchat.git
```
Step 4: Open the Project Folder
```
cd mchat
```
Step 5: Run the Installer
```
bash install.sh
```
The installer will install the required dependencies and configure the 
```
mchat
```
 command.

▶️ Run mChat

After installation, you can launch the application from any Termux directory:

*mchat*

📱 Main Menu

╔══════════════════════════════╗
║          mChat V2.6          ║
║       CYBER NEON EDITION     ║
╠══════════════════════════════╣
║  [1] Start Chat              ║
║  [2] User Profile            ║
║  [3] Settings                ║
║  [4] About mChat             ║
║  [0] Exit                    ║
╚══════════════════════════════╝

🔐 Account System

Users can:

- Create an account using email and password.
- Log in with an existing account.
- Use their own account in the global chat.

🌍 Global Chat

All registered users connect to the same Firebase-powered group chat.

💾 Local Data

Chat history and local configuration are stored on the device.

Updating the application does not intentionally remove existing local chat history or configuration.

🔄 Update mChat

To update the application:
```
cd ~/mchat
git pull
bash install.sh
```
Then launch:
```
mchat
```
🛠️ Technologies Used

- Python 3
- Firebase Authentication
- Firebase Realtime Database
- SQLite
- REST API
- Termux

🔒 Security

- Never share your account password or authentication tokens.
- Firebase Realtime Database Security Rules should be configured to protect user data.
- The Firebase Web API key is client configuration, not a private server credential.
- Never publish Firebase service account private keys or other server secrets.

👨‍💻 Developer

Developer: Sajol

Project: mChat

Version: 2.6

Edition: Cyber Neon

📜 License

This project is open-source. A license file should be added to the repository to specify the permissions and conditions for reuse.

---

⭐ If you like this project, give the repository a Star on GitHub

GitHub: https://github.com/appsajol/mchat.ggit
