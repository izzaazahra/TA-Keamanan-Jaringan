# -*- coding: utf-8 -*-
import os
import sys

def build_sentence_dictionary():
    len_map = {}
    subjects = [
        "kita ", "kita semua ", "langkah kita ", "seluruh langkah kita ",
        "hari-hari kita ", "kehidupan kita ", "setiap langkah hidup kita ",
        "perjalanan hari kita ", "setiap aktivitas keseharian kita "
    ]
    adverbs = [
        "selalu ", "senantiasa ", "akan selalu ", "tetap ",
        "dapat senantiasa "
    ]
    verbs = [
        "diberkahi ", "dilimpahi ", "disertai ", "dipenuhi ",
        "diberikan ", "diiringi "
    ]
    qualities = [
        "kesehatan, ", "kesehatan jasmani, ",
        "kebahagiaan, ", "kebahagiaan tulus, ",
        "kedamaian, ", "kedamaian hati, ",
        "kelancaran, ", "kelancaran rezeki, ",
        "semangat positif, ", "energi positif, ",
        "keberkahan, ", "limpahan keberkahan, "
    ]
    connectors = ["serta ", "dan ", "dan juga ", "serta limpahan "]
    endings = [
        "kebaikan dalam menjalani setiap rutinitas sehari-hari.",
        "kebahagiaan dalam menjalani kehidupan yang penuh makna.",
        "kebaikan di setiap detik yang kita lalui bersama.",
        "semangat untuk terus menebar manfaat bagi sesama.",
        "ketenangan jiwa dalam mengarungi hari-hari kita.",
        "rasa syukur atas setiap berkah yang kita terima.",
        "kehangatan dan kedamaian di dalam hati kita.",
        "semangat baru dalam menyambut hari esok yang cerah."
    ]

    for prefix in ["Semoga ", "Mari kita berharap agar "]:
        for subj in subjects:
            for adv in adverbs:
                for v in verbs:
                    for conn in connectors:
                        for end in endings:
                            for q in qualities:
                                candidate = f"{prefix}{subj}{adv}{v}{q}{conn}{end}"
                                b_len = len(candidate.encode('utf-8'))
                                if b_len not in len_map:
                                    len_map[b_len] = candidate
    return len_map

def compose_payload(sentences_pool, target_bytes, len_map):
    bridges = [
        "",
        "Hal ini sangat baik untuk kita. ",
        "Kebiasaan baik ini sangat bermanfaat bagi kita. ",
        "Langkah kecil ini membawa ketenangan jiwa kita. ",
        "Hal tersebut membantu pikiran tetap rileks dan segar. ",
        "Rutinitas ini memberi energi positif bagi raga kita. ",
        "Menjalani hari dengan tenang membuat hidup lebih indah dan bahagia. "
    ]
    
    current = ""
    for s in sentences_pool:
        # Check if adding this sentence keeps us under target - 86
        test_next = current + (s.strip() + " ")
        rem = target_bytes - len(test_next.encode('utf-8'))
        
        # Can we close directly?
        if 86 <= rem <= 175:
            return test_next + len_map[rem]
            
        # Can we close using one of our natural bridges?
        for b in bridges:
            rem_b = target_bytes - len((test_next + b).encode('utf-8'))
            if 86 <= rem_b <= 175:
                return test_next + b + len_map[rem_b]
                
        if rem < 86:
            # We reached near the target, try bridges on current
            for b in bridges:
                rem_b = target_bytes - len((current + b).encode('utf-8'))
                if 86 <= rem_b <= 175:
                    return current + b + len_map[rem_b]
            break
            
        current = test_next
        
    # If still not closed, try with bridges on current
    for b in bridges:
        rem_b = target_bytes - len((current + b).encode('utf-8'))
        if 86 <= rem_b <= 175:
            return current + b + len_map[rem_b]
            
    raise ValueError(f"Could not fit payload for target {target_bytes}")

def get_all_payloads():
    len_map = build_sentence_dictionary()
    
    # Pool of high-quality, rich sentences about daily life
    pool_pagi = [
        "Bangun lebih awal di pagi hari memberikan kesempatan berharga untuk menikmati keheningan alam sebelum kesibukan kota dimulai.",
        "Menghirup udara sejuk di teras rumah sambil memandangi tanaman hias yang hijau menyegarkan pandangan mata.",
        "Segelas air putih hangat di awal hari membantu melancarkan metabolisme tubuh dan membersihkan saluran pencernaan.",
        "Menyiapkan sarapan praktis seperti telur rebus atau sepiring nasi uduk hangat memberi energi yang cukup untuk beraktivitas.",
        "Mendengarkan kicauan burung di pepohonan sekitar rumah mengingatkan kita pada keindahan hal-hal sederhana dalam hidup.",
        "Merapikan tempat tidur dan membuka jendela kamar membiarkan sinar matahari pagi masuk memberi kehangatan alami.",
        "Melakukan peregangan otot selama lima menit membuat tubuh terasa lebih lentur dan siap menghadapi rutinitas harian.",
        "Menyapa anggota keluarga dengan senyuman hangat menciptakan suasana rumah yang penuh kedamaian dan kebersamaan.",
        "Menyiapkan daftar tugas yang perlu diselesaikan hari ini membantu pikiran tetap terarah dan tidak mudah cemas."
    ]
    
    pool_kerja = [
        "Perjalanan menuju kampus atau tempat kerja menjadi lebih santai jika kita berangkat sedikit lebih awal dari jadwal biasanya.",
        "Menikmati pemandangan kota di pagi hari atau mendengarkan siaran radio favorit dapat meredakan kepenatan selama di perjalanan.",
        "Tiba di tempat tujuan dengan hati yang tenang membuat kita lebih siap berdiskusi dan berinteraksi secara positif.",
        "Membersihkan meja kerja sebelum mulai bekerja membantu kita berkonsentrasi secara optimal pada pekerjaan penting.",
        "Menyapa rekan sejawat dengan ramah mempererat rasa persaudaraan dan menciptakan lingkungan kerja yang bersahabat.",
        "Menyelesaikan pekerjaan yang paling menantang terlebih dahulu merupakan strategi yang sangat efektif untuk menghemat energi mental.",
        "Mengambil jeda singkat setiap satu jam untuk mengistirahatkan mata dari layar komputer sangat baik bagi kesehatan penglihatan.",
        "Berdiskusi secara terbuka dengan rekan tim sering kali menghasilkan solusi kreatif untuk menyelesaikan kendala bersama.",
        "Mencatat hal-hal penting dalam rapat harian membantu kita mengingat setiap komitmen tugas dengan tepat dan teliti."
    ]
    
    pool_siang = [
        "Ketika waktu makan siang tiba, menyantap hidangan hangat bersama teman menjadi momen yang dinanti-nantikan.",
        "Memilih menu makan siang dengan sayuran segar dan lauk bergizi seimbang membantu tubuh tetap bertenaga hingga sore hari.",
        "Menghindari penggunaan ponsel saat makan membuat kita lebih menikmati rasa makanan dan menghargai teman di hadapan kita.",
        "Berjalan kaki sejenak di sekitar gedung kantor setelah makan siang membantu proses pencernaan dan melancarkan aliran darah.",
        "Menunaikan ibadah di tengah hari memberikan ketenangan batin yang memulihkan kembali kejernihan pikiran.",
        "Meneguk segelas air putih dingin di hari yang terik terasa sangat menyegarkan dan mengembalikan hidrasi tubuh.",
        "Menjaga suasana hati tetap gembira di paruh kedua hari membuat waktu bekerja terasa berlalu dengan cepat dan produktif."
    ]
    
    pool_sore = [
        "Sore hari membawa kesejukan tersendiri ketika bayangan matahari mulai memanjang ke arah timur.",
        "Menuntaskan tugas-tugas akhir sebelum jam pulang kerja memberikan rasa lega dan kepuasan tersendiri.",
        "Menikmati secangkir teh hangat atau kopi tubruk di sore hari menjadi teman yang pas untuk melepas rasa lelah.",
        "Banyak orang meluangkan waktu sore untuk berolahraga ringan seperti jogging di taman kota atau bersepeda santai.",
        "Perjalanan pulang ke rumah diiringi pemandangan senja yang indah menjadi penutup yang manis setelah seharian berkarya.",
        "Menatap langit jingga di ufuk barat mengingatkan kita bahwa hari ini telah dilalui dengan penuh perjuangan dan makna."
    ]
    
    pool_malam = [
        "Melangkah masuk ke dalam rumah dan disambut senyuman keluarga seketika menghapus segala rasa letih di tubuh.",
        "Mandi dengan air bersih yang segar mengembalikan kebugaran fisik dan membersihkan debu perjalanan.",
        "Makan malam bersama keluarga di meja makan menjadi ruang berbagi cerita tentang berbagai pengalaman menarik hari ini.",
        "Mendengarkan cerita anak atau pasangan dengan penuh perhatian memperkokoh rasa cinta dan keharmonisan keluarga.",
        "Meluangkan waktu santai di ruang tamu untuk menonton acara favorit atau membaca buku yang mendidik sangat menenangkan.",
        "Menjauhkan gawai setidaknya setengah jam sebelum tidur membantu otak beralih ke mode relaksasi yang alami.",
        "Menatap langit malam bertabur bintang memberi rasa damai dan kesadaran akan kebesaran semesta raya.",
        "Menulis beberapa hal positif yang kita syukuri hari ini di buku harian menumbuhkan pandangan hidup yang optimis.",
        "Berbaring di kasur yang nyaman dengan kamar yang sejuk membawa kita pada istirahat malam yang berkualitas."
    ]
    
    pool_filosofi = [
        "Kehidupan sehari-hari sesungguhnya tersusun dari serangkaian momen-momen kecil yang patut kita hargai dan syukuri.",
        "Kebahagiaan sejati tidak selalu terletak pada pencapaian besar, melainkan pada ketenangan hati dalam menjalani kesederhanaan.",
        "Menjaga hubungan baik dengan tetangga sekitar menciptakan rasa aman dan kebersamaan di lingkungan tempat tinggal kita.",
        "Saling tolong-menolong dalam kesulitan kecil menumbuhkan ikatan sosial yang kuat di tengah masyarakat kita.",
        "Belajar memaafkan kekeliruan kecil orang lain membuat hati kita terbebas dari beban amarah dan kedengkian.",
        "Menghabiskan akhir pekan dengan membersihkan pekarangan rumah atau menata tanaman menghadirkan kepuasan batin tersendiri.",
        "Menikmati makanan tradisional olahan sendiri mengajarkan kita untuk menghargai kekayaan kuliner warisan leluhur.",
        "Membiasakan gaya hidup hemat dan bersahaja membuat kita lebih mandiri dan tidak mudah terpengaruh tren sesaat.",
        "Kesehatan fisik dan kesehatan mental adalah dua anugerah terbesar yang harus senantiasa kita jaga dengan penuh kesadaran."
    ]

    all_sentences = pool_pagi + pool_kerja + pool_siang + pool_sore + pool_malam + pool_filosofi

    payloads = {}
    
    # 1. 10 Byte
    payloads[10] = "Ayo ngopi!"
    
    # 2. 50 Byte
    payloads[50] = "Jangan lupa sarapan pagi serta minumlah air putih."
    
    # 3. 100 Byte
    payloads[100] = "Hari ini cuaca sangat cerah, cocok untuk berjalan santai di taman kota sambil menikmati udara segar."
    
    # 4. 500 Byte
    payloads[500] = compose_payload(pool_pagi, 500, len_map)
    
    # 5. 1.000 Byte
    payloads[1000] = compose_payload(pool_kerja + pool_siang, 1000, len_map)
    
    # 6. 2.500 Byte
    payloads[2500] = compose_payload(pool_pagi + pool_kerja + pool_siang + pool_sore, 2500, len_map)
    
    # 7. 5.000 Byte
    payloads[5000] = compose_payload((pool_pagi + pool_kerja + pool_siang + pool_sore + pool_malam) * 2, 5000, len_map)
    
    # 8. 10.000 Byte
    payloads[10000] = compose_payload(all_sentences * 3, 10000, len_map)
    
    # 9. 25.000 Byte
    payloads[25000] = compose_payload(all_sentences * 7, 25000, len_map)
    
    # 10. 50.000 Byte
    payloads[50000] = compose_payload(all_sentences * 14, 50000, len_map)
    
    return payloads

if __name__ == '__main__':
    payloads = get_all_payloads()
    for size, text in sorted(payloads.items()):
        b_len = len(text.encode('utf-8'))
        print(f"Payload {size:5d} bytes: actual={b_len:5d} match={size==b_len} | preview: {text[:60]}... -> ...{text[-40:]}")
        assert size == b_len, f"Mismatch on {size}: {b_len}"
    print("\nSUCCESS: All 10 payloads generated and verified perfectly!")
