
from flask import Flask, config, request, send_file, Response
from flask_restful import reqparse,  Api, Resource
from pyapp.map.plot_map import plot_map
import datetime
from loguru import logger
from pyapp.utils import get_log_file, get_figures

parser_map_post = reqparse.RequestParser()
parser_map_post.add_argument('startlon', type=float)
parser_map_post.add_argument('startlat', type=float)
parser_map_post.add_argument('endlon', type=float)
parser_map_post.add_argument('endlat', type=float)

parser_map_get = reqparse.RequestParser()
parser_map_get.add_argument("filename", type=str)

logger.add(get_log_file())


class Map(Resource):
    def get(self):
        args = parser_map_get.parse_args()
        print(get_figures(args["filename"]))
        # send_file(get_figures(args["filename"]))
        resp = Response(
            open(get_figures(args["filename"]), 'rb'), mimetype="image/png")
        return resp

    def post(self):
        args = parser_map_post.parse_args()
        if(args["startlon"] == None or args["startlat"] == None or args["endlon"] == None or args["endlat"] == None):
            return "typeerror"
        ip = request.remote_addr
        thetime = f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}"
        filename = f"{ip}-{thetime}"
        result = plot_map(args["startlon"], args["startlat"],
                          args["endlon"], args["endlat"], filename)
        logger.info(f"generate figure for {ip} in {result}")
        return result


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=True)
    api = Api(app)

    # a simple page that says hello

    api.add_resource(Map, '/map')
    logger.info("start application")

    return app
