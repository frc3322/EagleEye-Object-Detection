from flask import Flask, send_file

app = Flask(__name__)


@app.route('/log')
def serve_text_file():
    print("Serving log file")
    try:
        return send_file('log.txt', mimetype='text/plain')
    except FileNotFoundError:
        return "File not found", 404


def run():
    app.run(debug=False)


if __name__ == '__main__':
    app.run(debug=True)
