from flask import Response

from utils import generate_printer_stream


@app.route('/printers', methods=['GET'])
def stream_printers():
    """
    GET endpoint that streams the discovery process in real time using SSE.
    """
    return Response(generate_printer_stream(), mimetype='text/event-stream')