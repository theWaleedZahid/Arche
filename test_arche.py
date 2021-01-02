# Arche FrameWork
# Tests for Testing Arche
# Developer: Waleed Zahid
import pytest

from api import API

def test_basic_route(api):
	@api.route("/home")
	def home(req, resp):
		resp.text = "This is a Test"

def test_route_overlap_throws_assertion(api):
	@api.route("/home")
	def home(req, resp):
		resp.text = "This is a Test"

	with pytest.raises(AssertionError):
		@api.route("/home")
		def home2(req, resp):
			resp.text = "This is a Route Overlap Test"

def test_arche_test_client_can_send_requests(api, client):
	RESP_TEXT = "This is Arche"

	@api.route('/hey')
	def cool(req, resp):
		resp.text = RESP_TEXT

	assert client.get("http://testserver/hey").text == RESP_TEXT

def test_parameterized_test_route(api, client):
	@api.route("/{name}")
	def hello(req, resp, name):
		resp.text = f"Hey, {name}"

	assert client.get("http://testserver/Arche").text == "Hey, Arche"
	assert client.get("http://testserver/Waleed").text == "Hey, Waleed"

def test_default_404_resp(client):
	response = client.get("http://testserver/does_not_exists")

	assert response.status_code == 404
	assert response.text == "OOPS! Your request page is not Found."

def test_alt_route(api, client):
	RESP_TEXT = "Alternative Route Adder"

	def home(req, resp):
		resp.text = RESP_TEXT

	api.add_route("/home", home)

	assert client.get("http://testserver/home").text == RESP_TEXT