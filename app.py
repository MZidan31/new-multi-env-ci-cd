from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    # Mengambil nilai variabel lingkungan APP_ENV, jika tidak ada akan menggunakan 'Unknown'
    environment = os.getenv('APP_ENV', 'Unknown')
    # Mengambil nama host dari container/pod (ini adalah ID replika di K8s)
    replica_id = os.getenv('HOSTNAME', 'Unknown')

    # Mengembalikan pesan sambutan yang menampilkan lingkungan dan ID replika
    return f"Halo dari aplikasi di lingkungan **{environment}**! Ini adalah replika: **{replica_id}**"

if __name__ == '__main__':
    # Menjalankan aplikasi Flask di semua antarmuka (0.0.0.0) pada port 5000
    app.run(host='0.0.0.0', port=5000)
