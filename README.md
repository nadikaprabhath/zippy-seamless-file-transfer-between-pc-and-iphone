<p align="center">
  <b>🚀 Zippy - Seamless File Transfer Between PC & iPhone</b>
</p>

<p align="center">
  <a href="https://github.com/nadikaprabhath" target="_blank">
    <img src="https://img.shields.io/badge/Follow-Nadika Prabhath-000000?style=for-the-badge&logo=github&logoColor=white" height="30">
  </a>
  <a href="https://t.me/your_telegram_link" target="_blank">
    <img src="https://img.shields.io/badge/Chat-Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" height="30">
  </a>
   <a href="https://www.linkedin.com/in/nadikaprabhath" target="_blank">
    <img src="https://img.shields.io/badge/Chat-linkendin-26A5E4?style=for-the-badge&logo=linkendin&logoColor=white" height="30">
  </a>
  <a href="https://github.com/nadikaprabhath/magnet-torrent-downloader/releases/tag/v1.0.0" target="_blank">
    <img src="https://img.shields.io/badge/Downloads-10-00C853?style=for-the-badge&logo=icloud&logoColor=white" height="30">
  </a>
  <a href="#" target="_blank">
    <img src="https://img.shields.io/badge/Commit_Activity-30/month-2962FF?style=for-the-badge&logo=git&logoColor=white" height="30">
  </a>
  <a href="#" target="_blank">
    <img src="https://img.shields.io/badge/Issues-1_closed-FFD54F?style=for-the-badge&logo=github&logoColor=black" height="30">
  </a>
</p>

Transfer files, photos, videos, and text between your PC and iPhone without any barriers
Features • Installation • Usage • Screenshots • Contributing
</div>

✨ Features

📱 Two-Way Transfer - Send files from PC to iPhone and vice versa
🖼️ Multi-Format Support - Images, videos, documents, audio files, and more
📝 Text Sharing - Quickly share notes and text snippets
🎨 Beautiful UI - Modern, responsive interface with glassmorphism design
⚡ Real-Time Updates - Automatic file list refresh and live notifications
📊 Upload Progress - Visual progress bars for file uploads
🗑️ Easy Management - Delete files directly from the web interface
🔄 Drag & Drop - Intuitive drag-and-drop file upload
🌐 Local Network - Works entirely on your WiFi network (no internet required)
🔒 Private - All transfers happen locally, no cloud storage involved

🎯 Supported File Types

Images: JPG, JPEG, PNG, GIF, HEIC
Videos: MP4, MOV, AVI
Audio: MP3, WAV, M4A
Documents: PDF, TXT, DOC, DOCX
Archives: ZIP, RAR

📋 Prerequisites

Python 3.7 or higher
PC and iPhone connected to the same WiFi network

🔧 Installation

Clone the repository

bash   git clone https://github.com/nadikaprabhath/zippy.git
   cd zippy

Install dependencies

bash   pip install flask flask-socketio watchdog

Run the application

bash   python app.py

Find your PC's IP address

Windows: Open Command Prompt and type ipconfig
Mac/Linux: Open Terminal and type ifconfig
Look for your IPv4 address (usually starts with 192.168.x.x)


Access from iPhone

Open Safari on your iPhone
Navigate to: http://YOUR_PC_IP:5000
Bookmark for quick access!



🎮 Usage
From PC to iPhone

Place files in the pc_to_iphone/ folder on your PC
Open the web interface on your iPhone
Go to the "Download" tab
Tap any file to download it to your iPhone

From iPhone to PC

Open the web interface on your iPhone
Go to the "Upload" tab
Choose files from your iPhone or use drag & drop
Files will appear in the iphone_to_pc/ folder on your PC

Text Sharing

Type or paste text in the text area on the Upload tab
Click "Share Text"
Text will be saved as a timestamped .txt file on your PC

📂 Folder Structure
zippy/
├── app.py                 # Main Flask application
├── pc_to_iphone/          # Files from PC (auto-created)
├── iphone_to_pc/          # Files from iPhone (auto-created)
└── README.md              # This file
🖼️ Screenshots
<div align="center">
Mobile Interface
Beautiful, responsive design optimized for iPhone
Upload Interface
Drag & drop or select files with progress tracking
File Management
Easy browsing and deletion of transferred files
</div>
🛠️ Technical Stack

Backend: Flask, Flask-SocketIO
Frontend: HTML5, TailwindCSS, Vanilla JavaScript
Real-time: WebSockets (Socket.IO)
File Monitoring: Watchdog
Security: Werkzeug secure filename handling

🔐 Security Notes

Zippy runs on your local network only
No data is sent to external servers
Files are transferred directly between your devices
Make sure your WiFi network is password-protected

🚨 Troubleshooting
Can't access from iPhone?

Verify both devices are on the same WiFi network
Check your PC's firewall settings (allow port 5000)
Try using your PC's IP address instead of localhost
Restart the Flask application

Files not appearing?

Click the refresh button (bottom right)
Check the console logs on your PC
Verify file permissions in the folders

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
👨‍💻 Developer
Nadika Prabhath

GitHub: @nadikaprabhath

⭐ Show Your Support
If you find this project useful, please consider giving it a star on GitHub!
🔮 Future Enhancements

 QR code for quick connection
 Multiple device support
 File preview functionality
 Transfer history
 Dark mode toggle
 Password protection option
 Bulk file operations


<div align="center">
Made with ❤️ by Nadika Prabhath
</div>

**Cannot access from other devices:**
- Check firewall settings
- Ensure devices are on the same network
- Verify the correct IP address is being used

**File not saving:**
- Check write permissions in the upload directory
- Ensure sufficient disk space

**iOS Shortcut not working:**
- Verify your laptop's IP address is correct
- Ensure the server is running
- Check that both devices are on the same Wi-Fi network
- Make sure the Request Body is set to "Form" type, not "File" or "JSON"

## Example Use Cases

- Quick file transfers between devices
- Mobile photo uploads to PC
- Simple document sharing in local networks
- Text snippet sharing between devices
- One-tap photo backup from iPhone to laptop

---

## Contributing
Fork the repo, make changes, and submit a pull request. Issues welcome at [github.com/nadikaprabhath/file-sharing-server-python](https://github.com/nadikaprabhath/file-sharing-server-python).

## License
MIT License. Copyright (c) 2025 Nadika Prabhath. See script header for details. 

