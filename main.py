import subprocess
import os

if __name__ == '__main__':
    # Порт Railway даёт через переменную окружения
    port = os.getenv('PORT', 8080)
    
    # Запускаем Shadowsocks сервер
    subprocess.run([
        'ssserver',
        '-s', '0.0.0.0',
        '-p', str(port),
        '-k', 'МойСложныйПароль123',
        '-m', 'chacha20-ietf-poly1305',
        '--workers', '1'
    ])
