from flask import Flask, jsonify, request
import threading
import scrapper
import csv

app = Flask(__name__)

scraper_thread = None
stop_event = threading.Event()
csv_file = "productosv3.csv"

def run_scraper():
    scrapper.main(stop_event)

@app.route('/iniciar', methods=['POST'])
def iniciar():
    global scraper_thread, stop_event
    if scraper_thread and scraper_thread.is_alive():
        return jsonify({"msg": "El scraper ya está corriendo"}), 400
    stop_event.clear()
    scraper_thread = threading.Thread(target=run_scraper)
    scraper_thread.start()
    return jsonify({"msg": "Scraper iniciado"}), 200

@app.route('/detener', methods=['POST'])
def detener():
    global stop_event
    if not scraper_thread or not scraper_thread.is_alive():
        return jsonify({"msg": "El scraper no está corriendo"}), 400
    stop_event.set()
    return jsonify({"msg": "Se solicitó detener el scraper"}), 200

@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify({"error": "Debes enviar el parámetro 'q' con el texto a buscar"}), 400

    resultados = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                
                ciudad = row.get("Ciudad", "").lower()
                region = row.get("Región", "").lower()
                region2 = row.get("Región2", "").lower()

                if query in ciudad or query in region or query in region2:
                    resultados.append(row)
    except FileNotFoundError:
        return jsonify({"error": f"El archivo {csv_file} no existe."}), 500

    if not resultados:
        return jsonify({"msg": f"No se encontraron resultados para '{query}'."}), 404

    return jsonify(resultados), 200


if __name__ == '__main__':
    app.run(port=5000)
