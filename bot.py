import os
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.secret_key = 'change_this_to_random_string_in_production'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 
                      'doc', 'docx', 'zip', 'mp3', 'wav', 'heic'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simple HTML page for browser uploads
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PC-iPhone Share</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        .upload-box { border: 2px dashed #ccc; padding: 40px; text-align: center; }
        button { background: #007AFF; color: white; padding: 15px 30px; 
                 border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0051D5; }
        #status { margin-top: 20px; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>📱 PC-iPhone File Share</h1>
    <div class="upload-box">
        <h3>Upload from Browser</h3>
        <input type="file" id="fileInput" multiple style="margin: 20px 0;">
        <br>
        <button onclick="uploadFile()">Upload Files</button>
    </div>
    
    <div class="upload-box" style="margin-top: 20px;">
        <h3>Share Text</h3>
        <textarea id="textInput" rows="4" style="width: 100%; padding: 10px;"></textarea>
        <br><br>
        <button onclick="uploadText()">Share Text</button>
    </div>
    
    <div id="status"></div>
    
    <script>
        function showStatus(message, isSuccess) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = isSuccess ? 'success' : 'error';
        }
        
        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            if (!fileInput.files.length) {
                showStatus('Please select a file', false);
                return;
            }
            
            const formData = new FormData();
            for (let file of fileInput.files) {
                formData.append('file', file);
            }
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.text();
                showStatus(result, response.ok);
                if (response.ok) fileInput.value = '';
            } catch (error) {
                showStatus('Upload failed: ' + error.message, false);
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
                const result = await response.text();
                showStatus(result, response.ok);
                if (response.ok) document.getElementById('textInput').value = '';
            } catch (error) {
                showStatus('Upload failed: ' + error.message, false);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in request', 400
    
    files = request.files.getlist('file')
    if not files or files[0].filename == '':
        return 'No file selected', 400
    
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid overwriting
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{name}_{timestamp}{ext}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_files.append(filename)
            print(f'✓ File saved: {filename}')
        else:
            return f'Invalid file type: {file.filename}', 400
    
    return f'Successfully uploaded {len(saved_files)} file(s)!', 200

@app.route('/upload/text', methods=['POST'])
def upload_text():
    try:
        text = request.data.decode('utf-8')
        if not text.strip():
            return 'No text received', 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'shared_text_{timestamp}.txt'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f'✓ Text saved: {filename}')
        return f'Text saved successfully as {filename}', 200
    
    except Exception as e:
        print(f'Error saving text: {e}')
        return f'Error: {str(e)}', 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'upload_folder': app.config['UPLOAD_FOLDER']})

if __name__ == '__main__':
    print(f'\n🚀 Server starting...')
    print(f'📁 Upload folder: {app.config["UPLOAD_FOLDER"]}')
    print(f'\n📱 On your iPhone, use this URL:')
    print(f'   http://YOUR_PC_IP:5000')
    print(f'\n💡 Find your PC IP with: ipconfig (Windows) or ifconfig (Mac/Linux)\n')
    
    app.run(host='0.0.0.0', port=5000, debug=True)