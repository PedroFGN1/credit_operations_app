from flask import render_template
from app import create_app
import threading
import webview
import requests
import time

# Cria a aplicação usando a factory definida em app/__init__.py
app = create_app()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def run_flask():
    # roda o servidor Flask em thread separada
    app.run(debug=False, port=5000)

if __name__ == "__main__":
    # inicia o Flask
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # espera o servidor subir antes de abrir a janela
    for _ in range(10):
        try:
            requests.get("http://127.0.0.1:5000")
            break
        except:
            time.sleep(0.5)

    # cria a janela desktop com PyWebView
    webview.create_window("Meu App Desktop", "http://127.0.0.1:5000", resizable=True)
    webview.start(http_server=True)