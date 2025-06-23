# Menggunakan image dasar Python 3.9 yang ramping dan berbasis Debian Buster
FROM python:3.9-slim-buster

# Mengatur direktori kerja di dalam container ke /app
WORKDIR /app

# Menyalin file requirements.txt dari host ke direktori kerja di container
COPY requirements.txt .

# Menginstal semua dependensi Python yang tercantum dalam requirements.txt
# --no-cache-dir untuk menghindari penyimpanan cache pip yang tidak perlu di dalam image
# -r requirements.txt untuk menginstal dari file requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin semua file dari direktori saat ini di host (proyek Anda) ke direktori kerja di container
COPY . .

# Memberi tahu Docker bahwa container akan mendengarkan pada port 5000 saat runtime
EXPOSE 5000

# Menentukan perintah yang akan dijalankan saat container dimulai
# Dalam kasus ini, menjalankan aplikasi Flask Anda
CMD ["python", "app.py"]
