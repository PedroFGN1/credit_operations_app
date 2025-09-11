import json
from flask import Blueprint, Response, jsonify, redirect, render_template, url_for
from app.logger_component import LoggerComponent

app_bp = Blueprint('app_bp', __name__, template_folder='templates')

log = LoggerComponent()

@app_bp.route('/')
def init():
    log.info("Aplicação iniciada!")
    return redirect(url_for("operation_bp.operacoes_de_credito"))

# --- Rota para o streaming de logs (Server-Sent Events) ---
@app_bp.route('/log-stream')
def log_stream():
    """Envia logs em tempo real para o frontend."""
    def generate():
        while True:
            # Pega uma mensagem da fila (espera se a fila estiver vazia)
            log_entry = log.log_queue.get()
            # Formata a mensagem para o padrão SSE
            sse_message = f"data: {json.dumps(log_entry)}\n\n"
            yield sse_message
    
    # Retorna uma resposta com o mimetype correto para SSE
    return Response(generate(), mimetype='text/event-stream')

# --- Rotas para gerenciar os logs ---
@app_bp.route('/logs/history')
def get_log_history():
    """Fornece o histórico de logs em formato JSON."""
    return jsonify(log.get_history())

@app_bp.route('/logs/clear', methods=['POST'])
def clear_logs():
    """Limpa o histórico de logs."""
    log.clear_history()
    return jsonify({"status": "success", "message": "Logs Limpos!"})