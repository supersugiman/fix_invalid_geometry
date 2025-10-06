Fix Invalid Geometry – Plugin QGIS

Fitur:
- Perbaiki vertex duplikat
- Perbaiki ring self-intersecting
- Simpan hasil ke file baru (GeoPackage, Shapefile, dll)

Cara Instal:
1. Tutup QGIS jika sedang berjalan.
2. Ekstrak file ZIP ini ke folder manapun.
3. Jalankan "installer.bat" sebagai pengguna biasa (tidak perlu admin).
4. Buka QGIS, lalu aktifkan plugin:
   Menu → Plugins → Manage and Install Plugins → Tab "Installed" → Centang "Fix Invalid Geometry (Save to File)"

Catatan:
- Plugin hanya bekerja di QGIS 3.16 atau lebih baru.
- Hasil perbaikan disimpan ke file baru, tidak mengubah data asli.

Catatan Keamanan
installer.bat tidak memerlukan hak admin — hanya menulis ke %APPDATA%.
Pastikan pengguna menutup QGIS sebelum instalasi agar tidak terjadi konflik file.
Dibuat untuk QGIS 3.34+.
