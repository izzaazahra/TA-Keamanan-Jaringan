import os
import random
import string
import pandas as pd
import matplotlib.pyplot as plt
from core import encode_image, decode_image, calculate_metrics
from PIL import Image
import numpy as np
import hashlib

# Pastikan ada gambar cover.png (ukuran minimal 512x512 disarankan)
COVER_IMAGE = 'cover.png'
PASSWORD = 'PasswordRahasia123'

if not os.path.exists(COVER_IMAGE):
    # Buat gambar dummy jika tidak ada (noise acak)
    dummy = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
    Image.fromarray(dummy).save(COVER_IMAGE)
    print("Cover image tidak ditemukan, membuat cover dummy (512x512).")

def random_text(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# 10 Ukuran Payload berbeda (bytes)
payload_sizes = [10, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
results = []

print("Memulai pengujian 10 payload...")
orig_img_arr = np.array(Image.open(COVER_IMAGE).convert('RGB'))

for i, size in enumerate(payload_sizes):
    payload = random_text(size)
    stego_path = f'stego_test_{size}.png'
    
    try:
        # Encode
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
        print(f"Payload {size} bytes: PSNR={psnr_val:.2f}, SSIM={ssim_val:.4f}, {is_match}")
        
        os.remove(stego_path) # Hapus file sementara
        
    except Exception as e:
        print(f"Gagal pada ukuran {size}: {e}")

# Simpan ke Tabel CSV
df = pd.DataFrame(results)
df.to_csv('hasil_evaluasi.csv', index=False)

# Buat Grafik
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(df["Ukuran Asli (Byte)"], df["PSNR (dB)"], marker='o', color='b', label='PSNR (dB)')
plt.xscale('log') # Skala logaritmik karena ukuran bervariasi
plt.ylabel('PSNR (dB)')
plt.title('Evaluasi Kualitas Citra Stego terhadap Ukuran Payload')
plt.grid(True)
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(df["Ukuran Asli (Byte)"], df["SSIM"], marker='s', color='g', label='SSIM')
plt.xscale('log')
plt.xlabel('Ukuran Payload (Bytes) - Skala Log')
plt.ylabel('SSIM')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('static/grafik_evaluasi.png')
print("\nEvaluasi selesai. Tabel disimpan di 'hasil_evaluasi.csv' dan grafik di 'grafik_evaluasi.png'.")
print(df.to_markdown(index=False))