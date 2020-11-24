
import datetime

from flask import Flask, Response, config, request, send_file
from flask_restful import Api, Resource, reqparse
from loguru import logger

from pyapp.map.plot_map import plot_map
from pyapp.vc.plot_vc import plot_vc
from pyapp.utils import get_figures, get_figures_vc, get_log_file

parser_map_post = reqparse.RequestParser()
parser_map_post.add_argument('startlon', type=float)
parser_map_post.add_argument('startlat', type=float)
parser_map_post.add_argument('endlon', type=float)
parser_map_post.add_argument('endlat', type=float)

parser_map_get = reqparse.RequestParser()
parser_map_get.add_argument("filename", type=str)

parser_vc_post = reqparse.RequestParser()
parser_vc_post.add_argument('startlon', type=float)
parser_vc_post.add_argument('startlat', type=float)
parser_vc_post.add_argument('endlon', type=float)
parser_vc_post.add_argument('endlat', type=float)
parser_vc_post.add_argument('parameter', type=str)
parser_vc_post.add_argument('x_axis_label', type=str)
parser_vc_post.add_argument('depth', type=float)
parser_vc_post.add_argument('colorbar_range', type=float, action='append')

parser_vc_get = reqparse.RequestParser()
parser_vc_get.add_argument("filename", type=str)

logger.add(get_log_file())


class Map(Resource):
    def get(self):
        args = parser_map_get.parse_args()
        resp = Response(
            open(get_figures(args["filename"]), 'rb'), mimetype="image/png")
        return resp

    def post(self):
        args = parser_map_post.parse_args()
        if(args["startlon"] == None or args["startlat"] == None or args["endlon"] == None or args["endlat"] == None):
            return "typeerror"
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip = request.remote_addr
        thetime = f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}"
        filename = f"{ip}-{thetime}-{args['startlon']}-{args['startlat']}-{args['endlon']}-{args['endlat']}"
        result = plot_map(args["startlon"], args["startlat"],
                          args["endlon"], args["endlat"], filename)
        logger.info(f"generate map for {ip} in {result}")
        return result


class Vc(Resource):
    def get(self):
        args = parser_vc_get.parse_args()
        resp = Response(
            open(get_figures_vc(args["filename"]), 'rb'), mimetype="image/png")
        return resp

    def post(self):
        args = parser_vc_post.parse_args()
        if(args["parameter"] == None or args["x_axis_label"] == None):
            return "typeerror"
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip = request.remote_addr
        thetime = f"{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}"
        filename = f"{ip}-{thetime}-{args['startlon']}-{args['startlat']}-{args['endlon']}-{args['endlat']}-{args['parameter']}-{args['x_axis_label']}-{args['depth']}-{args['colorbar_range'][0]}-{args['colorbar_range'][1]}"
        result = plot_vc(args['startlon'], args['startlat'],
                         args['endlon'], args['endlat'], args['parameter'], args['x_axis_label'], args['depth'], args['colorbar_range'], filename)
        logger.info(f"generate vc for {ip} in {result}")
        return result


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=True)
    api = Api(app)

    # a simple page that says hello

    api.add_resource(Map, '/map')
    api.add_resource(Vc, '/vc')
    logger.info("start application")

    return app
