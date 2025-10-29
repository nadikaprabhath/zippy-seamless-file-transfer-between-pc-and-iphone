import os
from flask import Flask, request, jsonify, render_template_string, send_file, abort
from werkzeug.utils import secure_filename
from datetime import datetime
import mimetypes

app = Flask(__name__)
app.config['SHARE_FOLDER'] = os.path.join(os.getcwd(), 'shared_files')
app.secret_key = 'change_this_to_random_string'

# Create shared folder if it doesn't exist
os.makedirs(app.config['SHARE_FOLDER'], exist_ok=True)

# HTML Interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PC to iPhone Share</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f7;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #1d1d1f; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #86868b; margin-bottom: 30px; }
        
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
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #86868b;
        }
        
        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 20px;
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
        }
        
        .refresh-btn:active {
            transform: scale(0.95);
        }
        
        .preview-img {
            max-width: 100%;
            max-height: 100px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 PC to iPhone</h1>
        <p class="subtitle">Files shared from your PC</p>
        
        <div id="fileList"></div>
    </div>
    
    <button class="refresh-btn" onclick="loadFiles()">🔄</button>
    
    <script>
        function getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            const icons = {
                'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'heic': '🖼️',
                'mp4': '🎥', 'mov': '🎥', 'avi': '🎥',
                'mp3': '🎵', 'wav': '🎵', 'm4a': '🎵',
                'pdf': '📄', 'doc': '📄', 'docx': '📄', 'txt': '📄',
                'zip': '📦', 'rar': '📦',
                'default': '📎'
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
        
        async function loadFiles() {
            try {
                const response = await fetch('/api/files');
                const files = await response.json();
                
                const fileList = document.getElementById('fileList');
                
                if (files.length === 0) {
                    fileList.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">📂</div>
                            <h3>No files yet</h3>
                            <p>Put files in the 'shared_files' folder on your PC</p>
                        </div>
                    `;
                    return;
                }
                
                fileList.innerHTML = '<div class="file-grid">' + files.map(file => {
                    const icon = getFileIcon(file.name);
                    const previewHtml = isImage(file.name) 
                        ? `<img src="/download/${encodeURIComponent(file.name)}" class="preview-img" onerror="this.style.display='none'">`
                        : '';
                    
                    return `
                        <a href="/download/${encodeURIComponent(file.name)}" class="file-card" download>
                            ${previewHtml}
                            <div class="file-icon">${icon}</div>
                            <div class="file-name">${file.name}</div>
                            <div class="file-size">${formatSize(file.size)}</div>
                        </a>
                    `;
                }).join('') + '</div>';
                
            } catch (error) {
                console.error('Error loading files:', error);
            }
        }
        
        // Load files on page load
        loadFiles();
        
        // Auto-refresh every 5 seconds
        setInterval(loadFiles, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/files')
def list_files():
    """API endpoint to list all files in shared folder"""
    try:
        files = []
        for filename in os.listdir(app.config['SHARE_FOLDER']):
            filepath = os.path.join(app.config['SHARE_FOLDER'], filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        
        # Sort by modified time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        return jsonify(files)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download a file from shared folder"""
    try:
        filepath = os.path.join(app.config['SHARE_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            abort(404)
        
        # Get mimetype for proper handling on iPhone
        mimetype = mimetypes.guess_type(filename)[0]
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
    
    except Exception as e:
        return str(e), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'share_folder': app.config['SHARE_FOLDER'],
        'file_count': len([f for f in os.listdir(app.config['SHARE_FOLDER']) 
                          if os.path.isfile(os.path.join(app.config['SHARE_FOLDER'], f))])
    })

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🚀 PC to iPhone File Share Server')
    print('='*60)
    print(f'\n📁 Share Folder: {app.config["SHARE_FOLDER"]}')
    print('\n📝 HOW TO USE:')
    print('   1. Put any files you want to share in the "shared_files" folder')
    print('   2. On your iPhone, open Safari and go to:')
    print(f'      http://YOUR_PC_IP:5000')
    print('\n💡 Find your PC IP address:')
    print('   Windows: ipconfig')
    print('   Mac/Linux: ifconfig or ip addr')
    print('\n⚠️  Make sure PC and iPhone are on the SAME WiFi network!')
    print('='*60 + '\n')
    
    app.run(host='0.0.0.0', port=5000, debug=True)