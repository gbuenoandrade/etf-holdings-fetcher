import http.server
import socketserver
import json

from vanguard import VanguardETFFetcher
from html_parser import HTMLParser
from chrome import ChromeDriver
from price import YahooPriceProvider
from etf import PositionFacade

PORT = 8000


class Server(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        components = self.path.split('/')
        if components[1] != 'api':
            self.send_response(404)
            self.end_headers()
            return

        ticker = components[-1]
        vanguard_fetcher = VanguardETFFetcher(ChromeDriver(), HTMLParser())
        price_provider = YahooPriceProvider()
        facade = PositionFacade(vanguard_fetcher, price_provider)
        positions, date = facade.calculate_positions(ticker)
        date_string = date.strftime('%d %b %Y')

        self._set_headers()
        data = {
            'date': date_string,
            'positions': [{'ticker': p.ticker, 'weight': p.weight} for p in positions]
        }
        self.wfile.write(json.dumps(data, indent=2).encode())

        vanguard_fetcher.quit()

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    @staticmethod
    def serve():
        with socketserver.TCPServer(("", PORT), Server) as httpd:
            print("Serving at port", PORT)
            httpd.serve_forever()
