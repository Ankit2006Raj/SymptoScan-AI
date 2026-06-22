import os
import socket
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def find_free_port(start_port=5001):
    """Finds an available port starting from the given port."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                port += 1

if __name__ == '__main__':
    # When debug=True, Flask spawns a child process using Werkzeug's reloader.
    # We only want to find a free port in the main parent process.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        port = find_free_port(5001)
        os.environ['FLASK_RUN_PORT'] = str(port)
        if port != 5001:
            print(f"\n⚠️  Port 5001 is in use. Automatically switching to port {port}...\n")
    else:
        # The child process reads the port assigned by the parent
        port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    
    app.run(debug=True, port=port)
