import os
import sys
from flask import Flask, render_template, jsonify, request


def get_frontend_path():
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'frontend')


def create_app():
    frontend_path = get_frontend_path()

    app = Flask(__name__,
                template_folder=os.path.join(frontend_path, 'templates'),
                static_folder=os.path.join(frontend_path, 'static'))

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/process', methods=['POST'])
    def process_data():
        try:
            data = request.json
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            input_value = data.get('input', '')
            result = input_value.upper() if input_value else 'No input'

            return jsonify({
                'result': f'Processed: {result}',
                'status': 'completed',
                'length': len(input_value)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/status/<code>')
    def status_code(code):
        """Return different status codes for testing"""
        try:
            status = int(code)
            return jsonify({'status': f'Returning {status}'}), status
        except ValueError:
            return jsonify({'error': 'Invalid status code'}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500

    return app
