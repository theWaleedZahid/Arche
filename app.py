# Arche Framework
# Main Class
# Developer: Waleed Zahid

PATH = "localhost"
PORT = 8000

from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
from middleware import Middleware
from api import API

app = API()

@app.route("/")
def home(request, response):
	response.text = "Hello from Arche"

@app.route("/template")
def template_handler(request, response):
	response.body = app.template("index.html", context={"name": "Arche", "title": "Best Framework"}).encode()

@app.route("/about")
def about(request, response):
	response.text = "Arche is a new python-based web-framework developed by Waleed Zahid"

@app.route("/hello/{name}")
def greet(request, response, name):
	response.text = f"Hello, {name}"

@app.route("/book")
class BooksHandler:
	"""This is a book handler"""
	def get(self, request, response):
		response.text = "Books Page"
	def post(self, request, response):
		response.text = "Endpoint of Books Class"

def custom_exception_handler(request, response):
	response.text = "OOPS! Something went wrong."

app.add_exception_handler(custom_exception_handler)


class SimpleCustomMiddleware(Middleware):
	def process_request(self, request):
		print("Processing Request: ", request.url)
	def process_response(self, request, response):
		print("Processing Response: ", request.url)

app.add_middleware(SimpleCustomMiddleware)

if __name__ == '__main__':
	httpd = make_server(PATH, PORT, app)
	print("Arche is being served at {} on port {}".format(PATH, PORT))
	print("Press Ctrl+C to Stop")
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print("Arche Server is Going to Sleep...")
		httpd.server_close()