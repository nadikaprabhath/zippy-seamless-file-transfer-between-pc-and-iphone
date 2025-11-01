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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://kit.fontawesome.com/yourcode.js" crossorigin="anonymous"></script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #F7FDFF;
            padding: 20px;
            padding-bottom: 100px;            
        
         .container { max-width: 1140px; width: 100%; margin: 0 auto; padding: 0 15px; }
        }
            
       
        h1 { color: #1d1d1f; margin-bottom: 10px; font-size: 28px; }
        
        .tabs {
            display: flex;
            justify-content: center;
            # gap: 50px;
            margin: 20px 0;
            # border: 2px solid #d2d2d7;
            border-radius: 120px;
            background: #E7E7E7;
            padding: 3px; 
        }
        
        .tab {
            # padding: 5px 10px;            
            border: none;
            font-size: 16px;
            color: #86868b;
            cursor: pointer;
            # transition: all 0.3s;
            border-radius: 120px;
            width: 100%;
            text-align: center;
        }
        
        .tab.active {
            color: black;
            font-wight: 700;
            background: white;
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
            # box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 2px solid #E8E8E8;
        }
        
        .upload-box {
            border: 2px dashed #007AFF;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            background: #F7FAFC;
            margin-bottom: 20px;
        }

        .upload-box:hover {
            background: #F5F7FF;
            animation: pulse 1.5s infinite;
            transition: all 0.3s;
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
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .file-card {
            display: flex;
            flex-direction: column;
            background: white;
            border-radius: 12px;
            text-align: center;
            # box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 2px solid #E8E8E8;
            cursor: pointer;
            transition: transform 0.2s;
            text-decoration: none;
            color: inherit;
            position: relative;
            overflow: hidden;
        }
        
        .file-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            # bg-white/80 backdrop-blur border-2 hover:border-blue-300
            background: white/80;
            backdrop-filter: blur(10px);
            border: 2px solid #007AFF;
            duration: 0.3s;
            transition: all 0.3s;
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
            text-align: start;
            margin: 0 15px 0 15px;
        }
        
        .file-size {
            font-size: 12px;
            color: #86868b;
            text-align: start;
            margin-left: 20px;
            margin-bottom: 20px;
            margin-top: 10px;
        }
        
        .preview-img {
            max-width: 100%;
            max-height: 200px;
            height: 200px;
            object-fit: cover;
            margin-bottom: 10px;
            overflow: hidden;
            border-bottom: 0.1px solid #d2d2d7;
        }
        
        .empty-state {
            text-align: center;
            # padding: 60px 20px;
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
    <div class="container">
        <h1 class="font-sans text-xl font-medium text-black flex items-center justify-center mt-3 mb-1 max-[375px]:justify-start sm:text-[25px] sm:pb-3">PC TO IPHONE DATA SHARE</h1>
        <p class="flex items-center justify-center mb-7 font-sans text-gray-500 text-center max-[375px]:text-[14px] sm:text-xl">Seamlessly transfer files between your devices</p>

        <div class="tabs sm:mt-10">
            <button class="tab active max-[375px]:p-3 p-2" onclick="switchTab('download')">
                <p class="max-[375px]:text-[13px]">From PC (Download)</p>
            </button>
            <button class="tab max-[375px]:p-3 p-2" onclick="switchTab('upload')">
                <p class="max-[375px]:text-[13px]">To PC (Upload)</p>
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
            <span style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">                
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-upload h-5 w-5 text-blue-600" aria-hidden="true"><path d="M12 3v12"></path><path d="m17 8-5-5-5 5"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path></svg>
                <h2>Upload Files</h2>
            </span>
                <div class="upload-box">
                    <div style="font-size: 48px; margin-bottom: 20px; align-items: center; justify-content: center; display: flex;">
                        <div class="p-4 bg-blue-100 rounded-full">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-file-up h-8 w-8 text-blue-600" aria-hidden="true"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M12 12v6"></path><path d="m15 15-3-3-3 3"></path></svg>
                        </div>
                    </div>
                    <p class="text-gray-400 max-[400px]:text-sm">Tap to select files from your iPhone</p>
                    <p class="mb-5 text-gray-400 max-[400px]:text-sm">Photos, Video, File</p>
                    <input type="file" id="fileInput" multiple accept="*/*">

                    <div class="flex gap-3 align-center justify-center">
                        <button onclick="document.getElementById('fileInput').click()" data-slot="button" class="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&amp;_svg]:pointer-events-none [&amp;_svg:not([class*='size-'])]:size-4 shrink-0 [&amp;_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive border bg-background text-foreground hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50 h-9 px-4 py-2 has-[&gt;svg]:px-3">Choose Files</button>
                        <button onclick="uploadFiles()" data-slot="button" class="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&amp;_svg]:pointer-events-none [&amp;_svg:not([class*='size-'])]:size-4 shrink-0 [&amp;_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive text-white text-primary-foreground h-9 px-4 py-2 has-[&gt;svg]:px-3 bg-blue-600 hover:bg-blue-700">Upload</button>
                    </div>
                </div>
                <div id="selectedFiles" style="margin: 10px 0; color: #86868b;"></div>
            </div>
            
            <div class="upload-section">
                <span style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">                
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-message-square h-5 w-5 text-green-600" aria-hidden="true"><path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"></path></svg>
                    <h2>Share Text/Notes</h2>
                </span>
                    <textarea id="textInput" class="border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 flex field-sizing-content w-full rounded-md border bg-input-background px-3 py-2 text-base transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm min-h-[120px] resize-y" placeholder="Type or paste text here.."></textarea>
                    <button onclick="uploadText()" class="inline-flex items-center justify-center mt-5 text-white whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&amp;_svg]:pointer-events-none [&amp;_svg:not([class*='size-'])]:size-4 shrink-0 [&amp;_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive text-primary-foreground h-9 px-4 py-2 has-[&gt;svg]:px-3 w-full bg-green-600 hover:bg-green-700">Share Text</button>         
            </div>            
            <div id="uploadStatus" class="status"></div>            
            <h2 style="margin: 30px 0 20px 0;">Your Uploaded Files</h2>
            <div id="uploadedFiles"></div>       
        </div>
        <div>
            <p class="text-xs text-gray-400 mt-10 mb-5 text-center">Developed by Nadika | <a href="https://github.com/nadikaprabhath/file-sharing-server-python-personel-.git" class="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">GitHub</a></p>
        </div>
    </div> 

    <button data-slot="button" onclick="loadAllFiles()" class="inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium disabled:pointer-events-none disabled:opacity-50 [&amp;_svg]:pointer-events-none [&amp;_svg:not([class*='size-'])]:size-4 shrink-0 [&amp;_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive bg-white text-primary-foreground hover:bg-primary/90 px-6 has-[&gt;svg]:px-4 fixed bottom-8 right-8 h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-all">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-refresh-cw h-5 w-5" aria-hidden="true"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
    </button>

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
                        <div data-slot="card" class="text-card-foreground flex flex-col gap-6 rounded-xl bg-white/60 backdrop-blur border-2 border-dashed">
                        <div class="flex flex-col items-center justify-center py-16 px-4">
                        <div class="p-6 bg-slate-100 rounded-full mb-4"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-folder-open h-12 w-12 text-slate-400" aria-hidden="true"><path d="m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2"></path></svg></div>
                        <h3 class="text-slate-900 mb-2">No files yet</h3>
                        <p class="text-slate-600 text-center max-w-md">${downloadPath === 'pc' ? 'Put files in "pc_to_iphone" folder on your PC' : 'Upload some files from your iPhone'}</p>
                        </div></div>
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