from flask import Flask, Response

from routes.print import printing_api

app = Flask(__name__)
app.register_blueprint(printing_api)

@app.route('/', methods=['GET'])
def printers_view():
    """
    HTML endpoint that displays the discovery stream graphically using SSE.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Printer Discovery Stream</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #stream { 
          white-space: pre-wrap; 
          border: 1px solid #ccc; 
          padding: 10px; 
          max-height: 400px; 
          overflow-y: scroll; 
          background-color: #f9f9f9;
        }
      </style>
    </head>
    <body>
      <h1>Live Printer Discovery</h1>
      <div id="stream">Connecting to printer discovery stream...</div>
      <script>
        const streamDiv = document.getElementById("stream");
        const evtSource = new EventSource("/printers");
        evtSource.onmessage = function(event) {
          streamDiv.innerHTML += event.data + "\\n";
          streamDiv.scrollTop = streamDiv.scrollHeight;
        };
        evtSource.onerror = function(event) {
          console.error("EventSource failed:", event);
          streamDiv.innerHTML += "\\nError in connection.";
        };
      </script>
    </body>
    </html>
    """
    return html_content

if __name__ == '__main__':
    app.run(debug=True, port=5000)