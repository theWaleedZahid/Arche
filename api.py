# Arche Framework
# API Class
# Developer: Waleed Zahid


import os
from jinja2 import Environment, FileSystemLoader
from webob import Request, Response
from parse import parse
from requests import Session as RequestSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from whitenoise import WhiteNoise
from middleware import Middleware
import inspect


class API:
	"""API Class of Arche Framework"""
	def __init__(self, templates_dir="templates", static_dir="static"):
		self.routes = {}
		self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)))
		self.exception_handler = None
		self.whitenoise = WhiteNoise(self._wsgi_app, root=static_dir)
		self.middleware = Middleware(self)

	def add_route(self, path, handler):
		assert path not in self.routes, "A route already exists"
		self.routes[path]=handler

	def route(self, path):
		assert path not in self.routes, "A route already exists"

		def wrapper(handler):
			self.add_route(path, handler)
			return handler

		return wrapper

	def _wsgi_app(self, env, start_response):
		request = Request(env)
		response = self.handle_request(request)

		return response(env, start_response)

	def __call__(self, env, start_response):
		path_info = env["PATH_INFO"]
		if path_info.startswith("/static"):
			env["PATH_INFO"] = path_info[len("/static"):]
			return self.whitenoise(env, start_response)
			
		return self.middleware(env, start_response)

	def handle_request(self, request):
		response = Response()

		try:
			handler, kwargs = self.find_handler(request_path=request.path)

			if handler is not None:
				if inspect.isclass(handler):
					handler = getattr(handler(), request.method.lower(), None)
					if handler is None:
						raise AttributeError("Method Not Allowed: ", request.method)
				handler(request, response, **kwargs)
			else:
				self.default_response(response)
		except Exception as e:
			if self.exception_handler is None:
				raise e
			else:
				self.exception_handler(request, response, e)
		
		return response

	def find_handler(self, request_path):
		for path, handler in self.routes.items():
			parse_result = parse(path, request_path)
			if parse_result is not None:
				return handler, parse_result.named

		return None,None


	def default_response(self, response):
		response.status_code = 404
		response.text = "OOPS! Your requested page is not Found."

	# TODO:
	def add_exception_handler(self, exception_handler):
		self.exception_handler = exception_handler


	def template(self, template_name, context=None):
		if context is None:
			context = {}

		return self.templates_env.get_template(template_name).render(**context)

	def add_middleware(self, middleware_cls):
		self.middleware.add(middleware_cls)


	# Test Session
	def test_session(self, base_url="http://testserver"):
		session = RequestSession()
		session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
		return session