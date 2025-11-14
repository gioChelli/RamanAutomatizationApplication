from raman_package import *
from Raman_server.server_raman import start_raman_server
import threading

def run_server():
    start_raman_server()

# Crea un thread per il server
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

window = ctkinter()

window.ctk.mainloop()