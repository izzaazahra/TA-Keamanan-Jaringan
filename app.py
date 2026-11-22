import os
from flask import Flask, render_template, request, url_for, jsonify, redirect
from core import encode_image, decode_image, calculate_metrics
from werkzeug.utils import secure_filename
from PIL import Image
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def handle_error(message, is_ajax=False):
    if is_ajax:
        return jsonify({'status': 'error', 'message': message}), 400
    return render_template('index.html', error_message=message), 400

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == 'GET':
        return redirect('/?tab=tool')

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
    
    if 'image' not in request.files:
        return handle_error("Error. Tidak ada gambar yang diunggah.", is_ajax)
    
    file = request.files['image']
    action = request.form.get('action', 'encode').strip().lower()
    password = request.form.get('password', '').strip()
    
    if file.filename == '':
        return handle_error("Error. Nama file gambar kosong. Harap pilih citra gambar.", is_ajax)
        
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    # Verifikasi keabsahan file citra menggunakan Pillow
    try:
        with Image.open(input_path) as img:
            real_format = (img.format or '').upper()
    except Exception:
        return handle_error("Error. File yang diunggah bukan format gambar yang valid atau file rusak.", is_ajax)

    try:
        if action in ['encode', 'enskripsi', 'enkripsi']:
            secret_text = request.form.get('secret_text', '').strip()
            if not secret_text:
                return handle_error("Error. Pesan rahasia wajib diisi sebelum memproses.", is_ajax)
            if not password:
                return handle_error("Error. Password wajib diisi untuk mengamankan data.", is_ajax)

            stego_filename = 'stego_' + filename.rsplit('.', 1)[0] + '.png'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], stego_filename)
            
            orig_arr, stego_arr, data_len = encode_image(input_path, secret_text, password, output_path)
            mse, psnr_val, ssim_val = calculate_metrics(orig_arr, stego_arr)
            
            return render_template('result.html', 
                                   action='Enskripsi', 
                                   orig_img=url_for('static', filename='uploads/' + filename),
                                   stego_img=url_for('static', filename='uploads/' + stego_filename),
                                   payload_size=data_len,
                                   mse=round(mse, 4),
                                   psnr=round(psnr_val, 2),
                                   ssim=round(ssim_val, 4),
                                   message="Data berhasil disisipkan dan dienskripsi!")
                                   
        elif action in ['decode', 'deskripsi', 'dekripsi']:
            # Pengecekan jika format gambar yang dikirim adalah JPG/JPEG
            if real_format in ['JPEG', 'MPO'] or filename.lower().endswith(('.jpg', '.jpeg', '.jfif')):
                return handle_error(
                    "Error. Gambar yang diunggah berformat JPG/JPEG. Steganografi LSB membutuhkan citra berformat PNG asli karena kompresi JPG merusak bit pesan rahasia.",
                    is_ajax
                )

            if not password:
                return handle_error("Error. Password wajib diisi untuk mendeskripsi pesan.", is_ajax)

            try:
                extracted_text = decode_image(input_path, password)
            except Exception:
                # Password salah atau LSB acak tidak cocok
                return handle_error(
                    "Error. Password yang dimasukkan salah.",
                    is_ajax
                )

            if not extracted_text:
                return handle_error(
                    "Error. Password yang dimasukkan salah.",
                    is_ajax
                )

            return render_template('result.html', 
                                   action='Deskripsi', 
                                   extracted_text=extracted_text,
                                   message="Data berhasil diekstrak dan dideskripsi!")
        else:
            return handle_error("Error. Aksi form tidak valid.", is_ajax)
                                   
    except ValueError as ve:
        err_msg = str(ve)
        if "terlalu besar" in err_msg.lower():
            return handle_error(
                "Error. Ukuran teks pesan rahasia melebihi kapasitas citra ini. Gunakan gambar dengan resolusi lebih tinggi atau kurangi panjang pesan.",
                is_ajax
            )
        return handle_error(f"Error. Gagal memproses data ({err_msg}).", is_ajax)
    except Exception as e:
        return handle_error(f"Error. Terjadi kesalahan saat memproses data ({str(e)}).", is_ajax)

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