import hashlib
import numpy as np
from PIL import Image
from Crypto.Cipher import AES  # type: ignore
from Crypto.Util.Padding import pad, unpad  # type: ignore
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

def get_key(password):
    # Menghasilkan kunci 256-bit dari password
    return hashlib.sha256(password.encode()).digest()

def encrypt_aes(data, password):
    key = get_key(password)
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    # Gabungkan IV dan Ciphertext
    return cipher.iv + ct_bytes

def decrypt_aes(enc_data, password):
    key = get_key(password)
    iv = enc_data[:16]
    ct = enc_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')

def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")

def encode_image(image_path, secret_data, password, output_path):
    image = Image.open(image_path).convert('RGB')
    img_array = np.array(image)
    
    # Enkripsi data
    encrypted_data = encrypt_aes(secret_data, password)
    
    # Tambahkan header (panjang data) dalam 32 bit
    data_len = len(encrypted_data)
    len_bin = format(data_len, '032b')
    
    # Konversi data terenkripsi ke binary
    bin_data = len_bin + ''.join(to_bin(encrypted_data))
    
    # Cek kapasitas
    max_capacity = img_array.size * 3 # RGB
    if len(bin_data) > max_capacity:
        raise ValueError(f"Data terlalu besar! Maksimal {max_capacity//8} bytes.")
    
    # Pengacakan posisi menggunakan password (untuk keamanan ekstra)
    np.random.seed(int(hashlib.md5(password.encode()).hexdigest(), 16) % (2**32))
    flat_img = img_array.flatten()
    indices = np.random.permutation(len(flat_img))[:len(bin_data)]
    
    # Sisipkan data ke LSB
    for i, bit in zip(indices, bin_data):
        flat_img[i] = (flat_img[i] & 254) | int(bit)
        
    stego_array = flat_img.reshape(img_array.shape)
    stego_image = Image.fromarray(stego_array.astype('uint8'))
    stego_image.save(output_path)
    
    return img_array, stego_array, data_len

def decode_image(stego_image_path, password):
    stego_image = Image.open(stego_image_path).convert('RGB')
    stego_array = np.array(stego_image)
    flat_img = stego_array.flatten()
    
    # Rekonstruksi posisi acak
    np.random.seed(int(hashlib.md5(password.encode()).hexdigest(), 16) % (2**32))
    indices = np.random.permutation(len(flat_img)) # Ambil semua posisi acak
    
    # Ekstrak 32 bit pertama untuk panjang data
    len_bin = ''.join([str(flat_img[indices[i]] & 1) for i in range(32)])
    data_len = int(len_bin, 2)
    
    # Ekstrak data sebenarnya
    bin_data = ''.join([str(flat_img[indices[i]] & 1) for i in range(32, 32 + (data_len * 8))])
    
    # Konversi binary ke bytes
    encrypted_data = bytes([int(bin_data[i:i+8], 2) for i in range(0, len(bin_data), 8)])
    
    # Dekripsi
    decrypted_text = decrypt_aes(encrypted_data, password)
    return decrypted_text

def calculate_metrics(original_array, stego_array):
    mse_val = np.mean((original_array - stego_array) ** 2)
    psnr_val = psnr(original_array, stego_array)
    ssim_val = ssim(original_array, stego_array, channel_axis=2)
    return mse_val, psnr_val, ssim_val