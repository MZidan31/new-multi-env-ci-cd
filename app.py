from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    environment = os.getenv('APP_ENV', 'Unknown')
    replica_id = os.getenv('HOSTNAME', 'Unknown')

    return f"Hello World dari aplikasi di lingkungan **{environment}**! Ini adalah replika: **{replica_id}**. Versi: 1.0 (Updated for Dev)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
