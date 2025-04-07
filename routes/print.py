from flask import Blueprint, request, jsonify
from escpos.printer import Network

printing_api = Blueprint('printing_api', __name__)

@printing_api.route('/print', methods=['POST'])
def print_job():
    printer = Network("127.0.0.1")
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No print data provided. Expected key "text".'}), 400

    if 'printer' in data:
        try:
            printer = Network(data['printer'])
        except Exception as e:
            print("Error initializing printer:", e)
            return jsonify({'error': 'Error while initializing printer'}), 500
    else:
        return jsonify({'error': 'No printer provided'}), 400

    if not printer:
        return jsonify({'error': 'Printer not initialized'}), 500

    try:
        text = data['text']
        # Send the text to the printer
        printer.text(text)

        return jsonify({'status': 'Print job completed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500