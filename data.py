import os
from flask import Flask, request, jsonify, render_template_string, send_file, abort
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes

app = Flask(__name__)

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
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f7;
            padding: 20px;
            padding-bottom: 100px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #1d1d1f; margin-bottom: 10px; font-size: 28px; }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            border-bottom: 2px solid #d2d2d7;
        }
        
        .tab {
            padding: 12px 24px;
            background: none;
            border: none;
            font-size: 16px;
            color: #86868b;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #007AFF;
            border-bottom-color: #007AFF;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .upload-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .upload-box {
            border: 2px dashed #007AFF;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            background: #f0f7ff;
            margin-bottom: 20px;
        }
        
        .upload-box input[type="file"] {
            display: none;
        }
        
        .upload-btn {
            background: #007AFF;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 5px;
        }
        
        .upload-btn:active {
            background: #0051D5;
        }
        
        textarea {
            width: 100%;
            padding: 15px;
            border: 1px solid #d2d2d7;
            border-radius: 8px;
            font-size: 16px;
            resize: vertical;
            min-height: 100px;
        }
        
        .file-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .file-card {
            background: white;
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.2s;
            text-decoration: none;
            color: inherit;
            position: relative;
        }
        
        .file-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .file-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        
        .file-name {
            font-size: 14px;
            color: #1d1d1f;
            word-break: break-word;
            margin-bottom: 5px;
        }
        
        .file-size {
            font-size: 12px;
            color: #86868b;
        }
        
        .preview-img {
            max-width: 100%;
            max-height: 100px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #86868b;
        }
        
        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #007AFF;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 30px;
            border: none;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(0,122,255,0.4);
            cursor: pointer;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="container" style="margin-bottom: 80px; color: #1d1d1f;">
        <h1>Two Way File Share</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('download')">
                From PC (Download)
            </button>
            <button class="tab" onclick="switchTab('upload')">
                To PC (Upload)
            </button>
        </div>
        
        <!-- Download from PC Tab -->
        <div id="download-tab" class="tab-content active">
            <h2 style="margin: 20px 0;">Files from your PC</h2>
            <div id="pcFiles"></div>
        </div>
        
        <!-- Upload to PC Tab -->
        <div id="upload-tab" class="tab-content">
            <div class="upload-section">
                <h2 style="margin-bottom: 10px;">Upload</h2>
                <div class="upload-box">
                    <div style="font-size: 48px; margin-bottom: 20px;">📁</div>
                    <p style="margin-bottom: 20px;">Tap to select files from your iPhone (Photos, Video, File)</p>
                    <input type="file" id="fileInput" multiple accept="*/*">
                    <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                        Choose Files
                    </button>
                    <button class="upload-btn" onclick="uploadFiles()" style="background: #34C759;">
                        Upload Selected
                    </button>
                </div>
                <div id="selectedFiles" style="margin: 10px 0; color: #86868b;"></div>
            </div>
            
            <div class="upload-section">
                <h2 style="margin-bottom: 10px;">Share Text/Notes</h2>
                <textarea id="textInput" placeholder="Type or paste text here..."></textarea>
                <button class="upload-btn" onclick="uploadText()" style="margin-top: 15px; width: 100%;">
                    Share Text
                </button>
            </div>
            
            <div id="uploadStatus" class="status"></div>
            
            <h2 style="margin: 30px 0 20px 0;">Your Uploaded Files</h2>
            <div id="uploadedFiles"></div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="loadAllFiles()">🔄</button>
    
    <script>
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
                'jpg': '', 'jpeg': '', 'png': '', 'gif': '', 'heic': '',
                'mp4': '', 'mov': '', 'avi': '',
                'mp3': '', 'wav': '', 'm4a': '',
                'pdf': '📄', 'doc': '📄', 'docx': '📄', 'txt': '📄',
                'zip': '📦', 'rar': '📦',
                'default': ''
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
        
        function renderFileGrid(files, container, downloadPath) {
            if (files.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div style="font-size: 64px; margin-bottom: 20px;">📂</div>
                        <h3>No files yet</h3>
                        <p>${downloadPath === 'pc' ? 'Put files in "pc_to_iphone" folder on your PC' : 'Upload some files from your iPhone'}</p>
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
                    <a href="/download/${downloadPath}/${encodeURIComponent(file.name)}" class="file-card" download>
                        ${previewHtml}
                        <div class="file-icon">${icon}</div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatSize(file.size)}</div>
                    </a>
                `;
            }).join('') + '</div>';
        }
        
        async function loadAllFiles() {
            try {
                // Load PC files
                const pcResponse = await fetch('/api/files/pc');
                const pcFiles = await pcResponse.json();
                renderFileGrid(pcFiles, document.getElementById('pcFiles'), 'pc');
                
                // Load uploaded files
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
            const files = this.files;
            if (files.length > 0) {
                const fileList = Array.from(files).map(f => f.name).join(', ');
                document.getElementById('selectedFiles').textContent = 
                    `Selected: ${fileList}`;
            }
        });
        
        async function uploadFiles() {
            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files.length) {
                showStatus('Please select files first', false);
                return;
            }
            
            const formData = new FormData();
            for (let file of fileInput.files) {
                formData.append('files', file);
            }
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    showStatus(`✓ Uploaded ${fileInput.files.length} file(s) successfully!`, true);
                    fileInput.value = '';
                    document.getElementById('selectedFiles').textContent = '';
                    loadAllFiles();
                } else {
                    const error = await response.text();
                    showStatus('Upload failed: ' + error, false);
                }
            } catch (error) {
                showStatus('Upload error: ' + error.message, false);
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
        return 'Text saved', 200
    
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
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
    
    app.run(host='0.0.0.0', port=5000, debug=True)