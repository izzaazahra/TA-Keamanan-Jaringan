import os
from flask import Flask, render_template, request, url_for
from core import encode_image, decode_image, calculate_metrics
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return "Tidak ada gambar yang diunggah", 400
    
    file = request.files['image']
    action = request.form['action']
    password = request.form['password']
    
    if file.filename == '':
        return "Nama file kosong", 400
        
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    try:
        if action == 'encode':
            secret_text = request.form['secret_text']
            stego_filename = 'stego_' + filename.rsplit('.', 1)[0] + '.png'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], stego_filename)
            
            orig_arr, stego_arr, data_len = encode_image(input_path, secret_text, password, output_path)
            mse, psnr_val, ssim_val = calculate_metrics(orig_arr, stego_arr)
            
            return render_template('result.html', 
                                   action='Encode', 
                                   orig_img=url_for('static', filename='uploads/' + filename),
                                   stego_img=url_for('static', filename='uploads/' + stego_filename),
                                   payload_size=data_len,
                                   mse=round(mse, 4),
                                   psnr=round(psnr_val, 2),
                                   ssim=round(ssim_val, 4),
                                   message="Data berhasil disisipkan!")
                                   
        elif action == 'decode':
            extracted_text = decode_image(input_path, password)
            return render_template('result.html', 
                                   action='Decode', 
                                   extracted_text=extracted_text,
                                   message="Data berhasil diekstrak dan didekripsi!")
                                   
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

@app.route('/evaluation')
def evaluation():
    try:
        # Membaca file CSV hasil evaluasi
        df = pd.read_csv('hasil_evaluasi.csv')
        # Mengubah data menjadi format list of dictionaries agar bisa dibaca HTML
        table_data = df.to_dict(orient='records')
        columns = df.columns.tolist()
        return render_template('evaluation.html', table_data=table_data, columns=columns)
    except FileNotFoundError:
        # Jika file belum ada, tampilkan pesan error
        return render_template('evaluation.html', error="Data evaluasi belum tersedia. Silakan jalankan 'python evaluate.py' terlebih dahulu.")

if __name__ == '__main__':
    app.run(debug=True, port=5000)