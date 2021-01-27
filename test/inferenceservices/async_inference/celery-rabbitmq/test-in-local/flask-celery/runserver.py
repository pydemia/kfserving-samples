import os
import argparse
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource

import model


app = Flask(__name__)
api = Api(app)


main_parser = argparse.ArgumentParser('Arguments for Container')
main_parser.add_argument(
    '--port', type=int, default=8500,
    dest='GRPC_PORT',
    help='GRPC_PORT'
)
main_parser.add_argument(
    '--rest_api_port', type=int, default=8501,
    dest='REST_API_PORT',
    help='REST_API_PORT'
)
main_parser.add_argument(
    '--model_name', type=str, default='microorganism', required=True,
    dest='MODEL_NAME',
    help='MODEL_NAME'
)
main_parser.add_argument(
    '--model_base_path', type=str, default='/models', required=True,
    dest='MODEL_BASE_PATH',
    help='MODEL_BASE_PATH'
)

main_args = main_parser.parse_args()
GRPC_PORT = main_args.GRPC_PORT
REST_PORT = main_args.REST_API_PORT  # 8501
MODEL_NAME = main_args.MODEL_NAME  # ${MODEL_NAME}
MODEL_PATH = main_args.MODEL_BASE_PATH  # ${MODEL_BASE_PATH}/${MODEL_NAME}

predict_fn = model.predict

# req_parser = reqparse.RequestParser()


class Serving(Resource):
    def post(self, predict):

        # req_args = req_parser.parse_args()

        json_data = request.get_json(force=True)

        # {
        #     'instances': [
        #         {'image_bytes': string, 'key': '1'}
        #     ]
        # }
        input_instances = json_data['instances']
        result = predict_fn(input_instances, MODEL_PATH)

        return result, 201


URL = os.path.join('/v1/models', MODEL_NAME + '<string:predict>')
api.add_resource(Serving, URL)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=REST_PORT)
