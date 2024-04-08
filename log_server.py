from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/log":
            try:
                with open("log.txt", "rb") as file:
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, "File Not Found: {}".format(self.path))
        else:
            self.send_error(404, "Not Found: {}".format(self.path))


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print("Starting server on localhost:{}...".format(port))
    httpd.serve_forever()


if __name__ == "__main__":
    run()
