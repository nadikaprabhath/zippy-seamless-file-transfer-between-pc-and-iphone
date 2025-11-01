import os
from flask import Flask, request, jsonify, render_template_string, send_file, abort
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes
from flask_socketio import SocketIO, emit
import watchdog.events
import watchdog.observers
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Two folders: one for PC→iPhone, one for iPhone→PC
app.config['PC_TO_IPHONE'] = os.path.join(os.getcwd(), 'pc_to_iphone')
app.config['IPHONE_TO_PC'] = os.path.join(os.getcwd(), 'iphone_to_pc')

# Create folders if they don't exist
os.makedirs(app.config['PC_TO_IPHONE'], exist_ok=True)
os.makedirs(app.config['IPHONE_TO_PC'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'heic', 
                      'mp4', 'mov', 'avi', 'mp3', 'wav', 'm4a',
                      'doc', 'docx', 'zip', 'rar'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML Interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PC ⟷ iPhone Share</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.js"></script>
    <script src="https://kit.fontawesome.com/yourcode.js" crossorigin="anonymous"></script>

    <style>
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 0.8; }
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(to bottom, #E0F2FE, #F3E8FF, #FFE4E6);
            padding: 16px;
            padding-bottom: 100px;
            overflow-x: hidden;
            position: relative;
            touch-action: manipulation; /* Improves touch responsiveness */
        }

        .orb {
            position: absolute;
            border-radius: 50%;
            opacity: 0.4;
            filter: blur(20px);
            animation: float 10s ease-in-out infinite, pulse 5s ease-in-out infinite;
        }

        .container { max-width: 1140px; width: 100%; margin: 0 auto; padding: 0 8px; }
        
        h1 { color: #1d1d1f; margin-bottom: 8px; font-size: 24px; text-align: center; }
        @media (min-width: 640px) { h1 { font-size: 28px; } }
        
        .tabs {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 16px 0;
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 9999px;
            padding: 4px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        @media (min-width: 640px) { 
            .tabs { flex-direction: row; justify-content: center; }
        }
        
        .tab {
            border: none;
            font-size: 14px;
            color: #6b7280;
            cursor: pointer;
            transition: all 0.2s; /* Faster transition */
            border-radius: 9999px;
            padding: 8px 16px;
            font-weight: 500;
            width: 100%;
            text-align: center;
            margin-bottom: 8px;
        }
        @media (min-width: 640px) { 
            .tab { width: auto; margin-bottom: 0; padding: 8px 24px; font-size: 16px; }
        }
        
        .tab.active {
            background: linear-gradient(to right, #3b82f6, #6366f1);
            color: white;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease; /* Faster animation */
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .upload-section {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            padding: 16px;
            margin: 16px 0;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05); /* Lighter shadow for performance */
            transition: all 0.2s;
        }

        .upload-section:hover {
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        }
        
        .upload-box {
            border: 2px dashed #93c5fd;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            background: rgba(255, 255, 255, 0.2);
            margin-bottom: 16px;
            transition: all 0.2s;
        }
        @media (min-width: 640px) { 
            .upload-box { padding: 40px; }
        }

        .upload-box.dragover {
            border-color: #3b82f6;
            background: rgba(59, 130, 246, 0.1);
            transform: scale(1.01); /* Smaller scale for faster feel */
        }

        .upload-box:hover {
            border-color: #3b82f6;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.01);
        }
        
        .upload-box input[type="file"] {
            display: none;
        }
        
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(209, 213, 219, 0.5);
            border-radius: 8px;
            font-size: 14px;
            resize: vertical;
            min-height: 100px;
            background: rgba(255, 255, 255, 0.5);
            transition: all 0.2s;
        }
        @media (min-width: 640px) { 
            textarea { padding: 15px; font-size: 16px; }
        }

        textarea:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }
        @media (min-width: 640px) { 
            .file-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; }
        }
        
        .file-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 12px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            color: inherit;
            position: relative;
            overflow: hidden;
            word-break: break-all; /* Fix bug: long names wrap */
        }
        @media (min-width: 640px) { 
            .file-card { padding: 16px; }
        }
        
        .file-card:hover {
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
        }

        .file-card::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 50%;
            background: linear-gradient(to top, rgba(255, 255, 255, 0.2), transparent);
            pointer-events: none;
        }
        
        .file-icon {
            font-size: 32px;
            margin-bottom: 4px;
            color: #6b7280;
        }
        @media (min-width: 640px) { 
            .file-icon { font-size: 48px; margin-bottom: 8px; }
        }
        
        .file-name {
            font-size: 12px;
            color: #1f2937;
            word-break: break-word;
            margin-bottom: 4px;
            text-align: center;
        }
        @media (min-width: 640px) { 
            .file-name { font-size: 14px; }
        }
        
        .file-size {
            font-size: 10px;
            color: #6b7280;
        }
        @media (min-width: 640px) { 
            .file-size { font-size: 12px; }
        }
        
        .preview-img {
            width: 100%;
            height: 80px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 4px;
        }
        @media (min-width: 640px) { 
            .preview-img { height: 120px; margin-bottom: 8px; }
        }
        
        .empty-state {
            text-align: center;
            color: #6b7280;
            padding: 24px;
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px dashed #93c5fd;
        }
        @media (min-width: 640px) { 
            .empty-state { padding: 40px; }
        }
        
        .status {
            padding: 8px;
            border-radius: 8px;
            margin: 8px 0;
            display: none;
            transition: opacity 0.3s;
        }
        @media (min-width: 640px) { 
            .status { padding: 12px; margin: 12px 0; }
        }
        
        .status.success {
            background: rgba(134, 239, 172, 0.3);
            color: #065f46;
            backdrop-filter: blur(4px);
        }
        
        .status.error {
            background: rgba(248, 113, 113, 0.3);
            color: #991b1b;
            backdrop-filter: blur(4px);
        }

        .delete-btn {
            position: absolute;
            top: 4px;
            right: 4px;
            background: rgba(239, 68, 68, 0.8);
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: all 0.2s;
            backdrop-filter: blur(4px);
        }
        @media (min-width: 640px) { 
            .delete-btn { top: 8px; right: 8px; width: 24px; height: 24px; font-size: 12px; }
        }

        .file-card:hover .delete-btn {
            opacity: 1;
        }

        .refresh-btn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: linear-gradient(to bottom right, #a855f7, #ec4899);
            color: white;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: none;
            font-size: 20px;
            box-shadow: 0 8px 24px rgba(168, 85, 247, 0.3);
            cursor: pointer;
            z-index: 1000;
            transition: all 0.2s;
        }
        @media (min-width: 640px) { 
            .refresh-btn { bottom: 32px; right: 32px; width: 56px; height: 56px; font-size: 24px; }
        }

        .refresh-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 32px rgba(168, 85, 247, 0.4);
        }

        .progress-item {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(12px);
            border-radius: 8px;
            padding: 8px;
            margin-top: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        @media (min-width: 640px) { 
            .progress-item { padding: 12px; }
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
            font-size: 12px;
            color: #1f2937;
        }
        @media (min-width: 640px) { 
            .progress-header { font-size: 14px; }
        }

        .progress-container {
            height: 6px;
            background: rgba(209, 213, 219, 0.3);
            border-radius: 4px;
            overflow: hidden;
        }
        @media (min-width: 640px) { 
            .progress-container { height: 8px; }
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(to right, #3b82f6, #6366f1);
            width: 0%;
            transition: width 0.2s ease;
        }

        .preview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
            gap: 6px;
            margin-top: 8px;
        }
        @media (min-width: 640px) { 
            .preview-grid { grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 8px; margin-top: 12px; }
        }

        .preview-item {
            position: relative;
        }

        .preview-thumbnail {
            width: 100%;
            height: 40px;
            object-fit: cover;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        @media (min-width: 640px) { 
            .preview-thumbnail { height: 60px; }
        }
    </style>
</head>

<body>
    <!-- Animated orbs -->
    <div class="orb w-96 h-96 bg-indigo-300 top-[-100px] left-[-100px] animation-delay-0"></div>
    <div class="orb w-80 h-80 bg-purple-300 top-[20%] right-[-80px] animation-delay-2000"></div>
    <div class="orb w-64 h-64 bg-pink-300 bottom-[-50px] left-[30%] animation-delay-4000"></div>
    <div class="orb w-48 h-48 bg-blue-300 bottom-[10%] right-[10%] animation-delay-6000"></div>

    <div class="container relative z-10">
        <h1 class="font-sans font-medium text-black flex items-center justify-center mb-1 sm:text-3xl text-2xl">PC — iPhone Share</h1>
        <p class="flex items-center justify-center mb-8 font-sans text-gray-500 text-center text-sm sm:text-xl sm:justify-center justify-start">Seamlessly transfer files and text between your devices with beautiful, modern interface</p>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('download')">
                <p class="text-sm sm:text-base">From PC (Download)</p>
            </button>
            <button class="tab" onclick="switchTab('upload')">
                <p class="text-sm sm:text-base">To PC (Upload)</p>
            </button>
        </div>
        
        <!-- Download from PC Tab -->
        <div id="download-tab" class="tab-content active">
            <h2 class="text-base sm:text-lg font-medium mb-4 sm:mb-6 pb-1 border-b-2 border-blue-500 w-fit mx-auto sm:mx-auto mx-0">Files from your PC</h2>
            <div id="pcFiles"></div>
        </div>
        
        <!-- Upload to PC Tab -->
        <div id="upload-tab" class="tab-content">
            <div class="upload-section">
                <span class="flex items-center gap-2 mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-600"><path d="M12 3v12"></path><path d="m17 8-5-5-5 5"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path></svg>
                    <h2 class="text-base sm:text-lg font-medium">Upload Files</h2>
                </span>
                <div class="upload-box" id="uploadBox">
                    <div class="flex justify-center mb-4">
                        <div class="p-3 bg-blue-100 rounded-full shadow-sm">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-600"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M12 12v6"></path><path d="m15 15-3-3-3 3"></path></svg>
                        </div>
                    </div>
                    <p class="text-gray-500 text-sm mb-1">Drag & drop files here or tap to select from your iPhone</p>
                    <p class="text-gray-500 text-sm mb-4">Photos, Videos, Files</p>
                    <input type="file" id="fileInput" multiple accept="*/*">

                    <div class="flex gap-3 justify-center">
                        <button onclick="document.getElementById('fileInput').click()" class="bg-white border border-gray-300 text-gray-700 px-3 py-1 sm:px-4 sm:py-2 rounded-md text-xs sm:text-sm font-medium hover:bg-gray-50 transition shadow-sm">Choose Files</button>
                        <button onclick="uploadFiles()" class="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-3 py-1 sm:px-4 sm:py-2 rounded-md text-xs sm:text-sm font-medium hover:from-blue-600 hover:to-indigo-700 transition shadow-sm">Upload</button>
                    </div>
                </div>
                <div class="text-gray-500 text-sm mt-2 truncate" id="selectedFiles"></div>
                <div id="previewGrid" class="preview-grid"></div>
                <div id="progressList"></div>
            </div>
            
            <div class="upload-section">
                <span class="flex items-center gap-2 mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-600"><path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"></path></svg>
                    <h2 class="text-base sm:text-lg font-medium">Share Text/Notes</h2>
                </span>
                <textarea id="textInput" class="border-gray-200/50 focus:border-blue-300 focus:ring-blue-200/50 min-h-[100px] resize-y text-sm sm:text-base" placeholder="Type or paste text here..."></textarea>
                <button onclick="uploadText()" class="mt-4 w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-1 sm:py-2 rounded-md text-xs sm:text-sm font-medium hover:from-green-600 hover:to-emerald-700 transition shadow-sm">Share Text</button>         
            </div>           
            <div id="uploadStatus" class="status truncate w-full overflow-hidden text-ellipsis whitespace-nowrap"></div>            
            <h2 class="text-base sm:text-lg font-medium mt-6 sm:mt-8 mb-4 sm:mb-6 pb-1 border-b-2 border-blue-500 w-fit mx-auto sm:mx-auto mx-0">Your Uploaded Files</h2>
            <div id="uploadedFiles"></div>       
        </div>
        <div class="text-center mt-8 sm:mt-10 mb-5">
            <p class="text-xs text-gray-500">Developed by Nadika | <a href="https://github.com/nadikaprabhath/file-sharing-server-python-personel-.git" class="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">GitHub</a></p>
        </div>
    </div> 

    <button class="refresh-btn flex items-center justify-center" onclick="loadAllFiles()">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5 sm:h-6 sm:w-6"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
    </button>

    <script>
        const socket = io();

        socket.on('new_file', function(data) {
            loadAllFiles();
            showStatus('New file added in ' + data.folder + ' folder!', true);
        });

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            
            if (tab === 'download') {
                document.querySelector('.tab:nth-child(1)').classList.add('active');
                document.getElementById('download-tab').classList.add('active');
            } else {
                document.querySelector('.tab:nth-child(2)').classList.add('active');
                document.getElementById('upload-tab').classList.add('active');
            }
            
            loadAllFiles();
        }
        
        function getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            const icons = {
                pdf: '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v4m0 0v4m-4-8h8m-8 0H4m4 0v8m8-8h4" /></svg>', // placeholder for pdf
                jpg: '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>',
                jpeg: '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>',
                png: '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>',
                gif: '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>',
                mp4: '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" /></svg>',
                // Add more as needed
                default: '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>'
            };
            return icons[ext] || icons['default'];
        }
        
        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        function isImage(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            return ['jpg', 'jpeg', 'png', 'gif'].includes(ext);
        }
        
        async function deleteFile(source, filename) {
            if (!confirm(`Are you sure you want to delete ${filename}?`)) return;
            
            try {
                const response = await fetch(`/delete/${source}/${encodeURIComponent(filename)}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    showStatus(`✓ Deleted ${filename} successfully!`, true);
                    loadAllFiles();
                } else {
                    const error = await response.text();
                    showStatus('Delete failed: ' + error, false);
                }
            } catch (error) {
                showStatus('Delete error: ' + error.message, false);
            }
        }
        
        function renderFileGrid(files, container, downloadPath) {
            if (files.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <svg class="h-12 w-12 sm:h-16 sm:w-16 text-gray-400 mb-2 sm:mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                        <h3 class="text-gray-700 font-medium mb-2 text-sm sm:text-base">No files yet</h3>
                        <p class="text-gray-500 text-xs sm:text-sm">${downloadPath === 'pc' ? 'Put files in "pc_to_iphone" folder on your PC' : 'Upload some files from your iPhone'}</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = '<div class="file-grid">' + files.map(file => {
                const icon = getFileIcon(file.name);
                const previewHtml = isImage(file.name) 
                    ? `<img src="/download/${downloadPath}/${encodeURIComponent(file.name)}" class="preview-img" onerror="this.style.display='none'">`
                    : '';
                
                return `
                    <div class="file-card">
                        <button class="delete-btn" onclick="deleteFile('${downloadPath}', '${file.name}')"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path><path d="M8 11v6"></path><path d="M16 11v6"></path></svg></button>
                        <a href="/download/${downloadPath}/${encodeURIComponent(file.name)}" class="flex flex-col items-center flex-1" download>
                            ${previewHtml}
                            <div class="file-icon">${icon}</div>
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${formatSize(file.size)}</div>
                        </a>
                    </div>
                `;
            }).join('') + '</div>';
        }
        
        async function loadAllFiles() {
            try {
                const pcResponse = await fetch('/api/files/pc');
                const pcFiles = await pcResponse.json();
                renderFileGrid(pcFiles, document.getElementById('pcFiles'), 'pc');
                
                const uploadResponse = await fetch('/api/files/iphone');
                const uploadFiles = await uploadResponse.json();
                renderFileGrid(uploadFiles, document.getElementById('uploadedFiles'), 'iphone');
            } catch (error) {
                console.error('Error loading files:', error);
            }
        }
        
        function showStatus(message, isSuccess) {
            const status = document.getElementById('uploadStatus');
            status.textContent = message;
            status.className = 'status ' + (isSuccess ? 'success' : 'error');
            status.style.display = 'block';
            setTimeout(() => status.style.display = 'none', 5000);
        }
        
        document.getElementById('fileInput').addEventListener('change', function() {
            updateSelectedFiles(this.files);
        });
        
        function updateSelectedFiles(files) {
            const selectedFilesEl = document.getElementById('selectedFiles');
            const previewGrid = document.getElementById('previewGrid');
            previewGrid.innerHTML = '';
            selectedFilesEl.textContent = '';

            if (files.length > 0) {
                const fileList = Array.from(files).map(f => f.name).join(', ');
                selectedFilesEl.textContent = `Selected: ${fileList}`;

                Array.from(files).forEach(file => {
                    if (file.type.startsWith('image/')) {
                        const url = URL.createObjectURL(file);
                        const div = document.createElement('div');
                        div.className = 'preview-item';
                        div.innerHTML = `<img src="${url}" class="preview-thumbnail" alt="${file.name}">`;
                        previewGrid.appendChild(div);
                    }
                });
            }
        }
        
        async function uploadFiles() {
            const fileInput = document.getElementById('fileInput');
            const files = Array.from(fileInput.files);
            if (files.length === 0) {
                showStatus('Please select files first', false);
                return;
            }

            const progressList = document.getElementById('progressList');
            progressList.innerHTML = '';
            let completed = 0;

            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const progressItem = document.createElement('div');
                progressItem.className = 'progress-item';
                progressItem.innerHTML = `
                    <div class="progress-header">
                        <span>${file.name} (${formatSize(file.size)})</span>
                        <span id="percent_${i}">0%</span>
                    </div>
                    <div class="progress-container">
                        <div id="bar_${i}" class="progress-bar"></div>
                    </div>
                `;
                progressList.appendChild(progressItem);

                try {
                    const formData = new FormData();
                    formData.append('files', file);

                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/upload', true);

                    xhr.upload.onprogress = (event) => {
                        if (event.lengthComputable) {
                            const percent = Math.round((event.loaded / event.total) * 100);
                            document.getElementById(`bar_${i}`).style.width = percent + '%';
                            document.getElementById(`percent_${i}`).textContent = percent + '%';
                        }
                    };

                    await new Promise((resolve, reject) => {
                        xhr.onload = () => {
                            if (xhr.status === 200) {
                                completed++;
                                if (completed === files.length) {
                                    showStatus(`✓ Uploaded ${files.length} file(s) successfully!`, true);
                                    fileInput.value = '';
                                    updateSelectedFiles([]);
                                    loadAllFiles();
                                    progressList.innerHTML = '';
                                }
                                resolve();
                            } else {
                                showStatus(`Upload failed for ${file.name}`, false);
                                reject();
                            }
                        };
                        xhr.onerror = () => {
                            showStatus(`Upload error for ${file.name}`, false);
                            reject();
                        };
                        xhr.send(formData);
                    });
                } catch (error) {
                    showStatus(`Error uploading ${file.name}: ${error.message}`, false);
                }
            }
        }
        
        async function uploadText() {
            const text = document.getElementById('textInput').value;
            if (!text.trim()) {
                showStatus('Please enter some text', false);
                return;
            }
            
            try {
                const response = await fetch('/upload/text', {
                    method: 'POST',
                    headers: {'Content-Type': 'text/plain'},
                    body: text
                });
                
                if (response.ok) {
                    showStatus('✓ Text shared successfully!', true);
                    document.getElementById('textInput').value = '';
                    loadAllFiles();
                } else {
                    showStatus('Failed to share text', false);
                }
            } catch (error) {
                showStatus('Error: ' + error.message, false);
            }
        }

        // Drag and drop functionality
        const uploadBox = document.getElementById('uploadBox');
        const fileInput = document.getElementById('fileInput');

        uploadBox.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadBox.classList.add('dragover');
        });

        uploadBox.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadBox.classList.remove('dragover');
        });

        uploadBox.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadBox.classList.remove('dragover');
            const droppedFiles = e.dataTransfer.files;
            fileInput.files = droppedFiles;
            updateSelectedFiles(droppedFiles);
            // Optionally auto-upload: uploadFiles();
        });
        
        // Load files on page load
        loadAllFiles();
        
        // Auto-refresh every 5 seconds
        setInterval(loadAllFiles, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/files/<source>')
def list_files(source):
    """List files from either pc or iphone folder"""
    try:
        folder = app.config['PC_TO_IPHONE'] if source == 'pc' else app.config['IPHONE_TO_PC']
        files = []
        
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        
        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify(files)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<source>/<filename>')
def download_file(source, filename):
    """Download a file"""
    try:
        folder = app.config['PC_TO_IPHONE'] if source == 'pc' else app.config['IPHONE_TO_PC']
        filepath = os.path.join(folder, filename)
        
        if not os.path.exists(filepath):
            abort(404)
        
        mimetype = mimetypes.guess_type(filename)[0]
        return send_file(filepath, as_attachment=True, download_name=filename, mimetype=mimetype)
    
    except Exception as e:
        return str(e), 500

@app.route('/delete/<source>/<filename>', methods=['DELETE'])
def delete_file(source, filename):
    """Delete a file"""
    try:
        folder = app.config['PC_TO_IPHONE'] if source == 'pc' else app.config['IPHONE_TO_PC']
        filepath = os.path.join(folder, filename)
        
        if not os.path.exists(filepath):
            abort(404)
        
        os.remove(filepath)
        print(f'Deleted: {filename} from {source}')
        return 'File deleted', 200
    
    except Exception as e:
        return str(e), 500

@app.route('/upload', methods=['POST'])
def upload_files():
    """Upload files from iPhone to PC"""
    if 'files' not in request.files:
        return 'No files in request', 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return 'No files selected', 400
    
    saved = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            filepath = os.path.join(app.config['IPHONE_TO_PC'], filename)
            file.save(filepath)
            saved.append(filename)
            print(f'✓ Received from iPhone: {filename}')
    
    socketio.emit('new_file', {'folder': 'iphone'})
    return f'Uploaded {len(saved)} file(s)', 200

@app.route('/upload/text', methods=['POST'])
def upload_text():
    """Upload text from iPhone to PC"""
    try:
        text = request.data.decode('utf-8')
        if not text.strip():
            return 'No text received', 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'text_{timestamp}.txt'
        filepath = os.path.join(app.config['IPHONE_TO_PC'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f'✓ Text received from iPhone: {filename}')
        socketio.emit('new_file', {'folder': 'iphone'})
        return 'Text saved', 200
    
    except Exception as e:
        return str(e), 500

class FileCreatedHandler(watchdog.events.FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f'New file in pc_to_iphone: {event.src_path}')
            socketio.emit('new_file', {'folder': 'pc'})

if __name__ == '__main__':
    observer = watchdog.observers.Observer()
    observer.schedule(FileCreatedHandler(), path=app.config['PC_TO_IPHONE'], recursive=False)
    observer.start()

    print('\n' + '='*70)
    print('🚀 TWO-WAY FILE SHARING: PC ⟷ iPhone')
    print('='*70)
    print(f'\n📁 Folders created:')
    print(f'   • pc_to_iphone/   (Put files here to share TO iPhone)')
    print(f'   • iphone_to_pc/   (Files from iPhone appear here)')
    print('\n📱 HOW TO USE:')
    print('   1. Find your PC IP: ipconfig (Windows) or ifconfig (Mac)')
    print('   2. On iPhone Safari, go to: http://YOUR_PC_IP:5000')
    print('   3. Two tabs:')
    print('      • "From PC" - Download files from PC')
    print('      • "To PC" - Upload files to PC')
    print('\n⚠️  Both devices must be on SAME WiFi!')
    print('='*70 + '\n')
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

    observer.stop()
    observer.join()