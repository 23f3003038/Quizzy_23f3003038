from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    @app.after_request
    def add_cors(resp):
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        resp.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return resp 

    @app.route('/ping')
    def ping():
        return jsonify({"message": "pong"})
    return app

if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0', port=5000)
