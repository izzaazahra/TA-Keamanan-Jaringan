import os
import random
import string
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from core import encode_image, decode_image, calculate_metrics
from PIL import Image
import numpy as np
import hashlib

# Pastikan direktori gambar evaluasi tersedia
EVAL_DIR = os.path.join('static', 'eval_images')
os.makedirs(EVAL_DIR, exist_ok=True)

# Pastikan ada gambar cover.png
COVER_IMAGE = 'cover.png'
PASSWORD = 'PasswordRahasia123'

if not os.path.exists(COVER_IMAGE):
    # Buat gambar dummy jika tidak ada (noise acak)
    dummy = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
    Image.fromarray(dummy).save(COVER_IMAGE)
    print("Cover image tidak ditemukan, membuat cover dummy (512x512).")

# Salin citra cover ke static/eval_images agar dapat diakses web
shutil.copy(COVER_IMAGE, os.path.join(EVAL_DIR, 'cover.png'))

from generate_payloads import get_all_payloads

# 10 Ukuran Payload berbeda (bytes)
payload_sizes = [10, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
payload_dict = get_all_payloads()
results = []

print("Memulai pengujian 10 payload dengan teks bermakna kehidupan sehari-hari...")
orig_img_arr = np.array(Image.open(COVER_IMAGE).convert('RGB'))

for i, size in enumerate(payload_sizes):
    payload = payload_dict[size]
    stego_filename = f'stego_payload_{size}.png'
    stego_path = os.path.join(EVAL_DIR, stego_filename)
    
    try:
        # Encode & simpan citra stego
        _, stego_arr, enc_size = encode_image(COVER_IMAGE, payload, PASSWORD, stego_path)
        
        # Hitung Metrik
        mse, psnr_val, ssim_val = calculate_metrics(orig_img_arr, stego_arr)
        
        # Decode & Verifikasi (BER / Hash)
        extracted = decode_image(stego_path, PASSWORD)
        hash_orig = hashlib.sha256(payload.encode()).hexdigest()
        hash_ext = hashlib.sha256(extracted.encode()).hexdigest()
        is_match = "Match" if hash_orig == hash_ext else "Failed"
        
        results.append({
            "No": i+1,
            "Ukuran Asli (Byte)": size,
            "Ukuran Encrypt (Byte)": enc_size,
            "MSE": round(mse, 4),
            "PSNR (dB)": round(psnr_val, 2),
            "SSIM": round(ssim_val, 4),
            "BER/Hash": is_match
        })
        print(f"Payload {size} bytes: MSE={mse:.4f}, PSNR={psnr_val:.2f}, SSIM={ssim_val:.4f}, {is_match}")
        
    except Exception as e:
        print(f"Gagal pada ukuran {size}: {e}")

# Simpan ke Tabel CSV
df = pd.DataFrame(results)
df.to_csv('hasil_evaluasi.csv', index=False)

# Buat Grafik 3 Metrik (MSE, PSNR, SSIM)
plt.figure(figsize=(10, 9))

# Subplot 1: MSE
plt.subplot(3, 1, 1)
plt.plot(df["Ukuran Asli (Byte)"], df["MSE"], marker='^', color='#dc2626', linewidth=2, label='MSE (Mean Squared Error)')
plt.xscale('log')
plt.ylabel('MSE', fontsize=10)
plt.title('Evaluasi Kualitas Citra Stego terhadap Ukuran Payload', fontsize=12, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper left')

# Subplot 2: PSNR
plt.subplot(3, 1, 2)
plt.plot(df["Ukuran Asli (Byte)"], df["PSNR (dB)"], marker='o', color='#2563eb', linewidth=2, label='PSNR (dB)')
plt.xscale('log')
plt.ylabel('PSNR (dB)', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right')

# Subplot 3: SSIM
plt.subplot(3, 1, 3)
plt.plot(df["Ukuran Asli (Byte)"], df["SSIM"], marker='s', color='#16a34a', linewidth=2, label='SSIM')
plt.xscale('log')
plt.xlabel('Ukuran Payload (Bytes) - Skala Log', fontsize=10)
plt.ylabel('SSIM', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='lower left')

plt.tight_layout()
plt.savefig(os.path.join('static', 'grafik_evaluasi.png'), dpi=150)
print("\nEvaluasi selesai. Citra stego disimpan di 'static/eval_images/', tabel di 'hasil_evaluasi.csv', dan grafik di 'static/grafik_evaluasi.png'.")
print(df.to_string(index=False))
