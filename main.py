from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import os
import uuid
import glob
import shutil
from PIL import Image, ImageDraw

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"  # replace with your directory
app.config['OUTPUT_FOLDER'] = os.path.join(app.static_folder, 'output')

def delete_contents_in_folder(dir_path):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # remove file or link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove directory
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

delete_contents_in_folder('static/')
delete_contents_in_folder('uploads/')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        delete_contents_in_folder('static/')
        delete_contents_in_folder('uploads/')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            im1 = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            # Run YOLOv8 model on the uploaded image
            model = YOLO("yolov8l-seg.pt")  # replace "model.pt" with your model's name
            results = model.predict(source=im1, save= True, project='static', name='output')

            outputFilePath = os.path.join('static', 'output', filename)
            outputFilePath.replace('\\', '/')


            
            return render_template('result.html', filename=outputFilePath)
            
    return render_template('upload.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
