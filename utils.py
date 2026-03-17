# ==========================================
# PENAMBAHAN FUNGSI GRID LAYOUT (MATEMATIKA PRESISI FINAL)
# ==========================================
def apply_grid_layout(packages):
    count = len(packages)
    if count == 0:
        return

    # Algoritma Penentu Kolom & Baris
    cols = 1
    while (cols * cols) < count:
        cols += 1
    rows = (count + cols - 1) // cols

    W, H = 1280, 720

    # KUNCI UTAMA: Menentukan Area Aman
    TOP_MARGIN = 60    # Turunkan 60px agar terhindar dari Status Bar & jam Android
    BOTTOM_MARGIN = 45 # Naikkan 45px agar terhindar dari tombol navigasi bawah
    GAP = 2            # Jarak antar jendela aplikasi (tipis)

    # Menghitung Ruang yang Benar-Benar Bisa Dipakai
    USABLE_W = W
    USABLE_H = H - TOP_MARGIN - BOTTOM_MARGIN

    cellW = USABLE_W // cols
    cellH = USABLE_H // rows

    script_content = "#!/system/bin/sh\n"
    for i, pkg in enumerate(sorted(packages)):
        c, r = i % cols, i // cols
        
        # Perhitungan Mutlak Anti-Tumpuk
        L = (c * cellW) + GAP
        R = ((c + 1) * cellW) - GAP
        
        # Titik Top dimulai dari TOP_MARGIN, lalu ditambah urutan barisnya
        T = TOP_MARGIN + (r * cellH) + GAP
        B = TOP_MARGIN + ((r + 1) * cellH) - GAP
        
        script_content += f"""
echo "-> Memproses {pkg}"
am force-stop {pkg}

PREF_FILE="/data/data/{pkg}/shared_prefs/{pkg}_preferences.xml"
TMP_FILE="/data/local/tmp/prefs.tmp"

grep -v 'app_cloner_current_window_' $PREF_FILE | grep -v '</map>' > $TMP_FILE 2>/dev/null

check_file=$(cat $TMP_FILE 2>/dev/null)
if [ -z "$check_file" ]; then
    echo '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>' > $TMP_FILE
    echo '<map>' >> $TMP_FILE
fi

echo '    <int name="app_cloner_current_window_left" value="{L}" />' >> $TMP_FILE
echo '    <int name="app_cloner_current_window_top" value="{T}" />' >> $TMP_FILE
echo '    <int name="app_cloner_current_window_right" value="{R}" />' >> $TMP_FILE
echo '    <int name="app_cloner_current_window_bottom" value="{B}" />' >> $TMP_FILE
echo '</map>' >> $TMP_FILE

mv $TMP_FILE $PREF_FILE

OWNER=$(ls -ld /data/data/{pkg} | awk '{{print $3}}')
chown $OWNER:$OWNER $PREF_FILE
chmod 660 $PREF_FILE

monkey -p {pkg} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1
sleep 4
"""

    # Buat file secara lokal
    local_path = "temp_grid.sh"
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Kopi ke SDCARD agar Root membacanya tanpa error direktori
    import os # memastikan os terpanggil
    os.system(f"cp {local_path} /sdcard/run_grid.sh")
    os.system("su -c 'sh /sdcard/run_grid.sh'")
    
    # Bersihkan sampah
    os.system("su -c 'rm /sdcard/run_grid.sh'")
    if os.path.exists(local_path):
        os.remove(local_path)
