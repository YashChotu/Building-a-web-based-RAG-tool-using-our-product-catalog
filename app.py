from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
import pandas as pd
from vector_store import VectorStore

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize vector store
vector_store = VectorStore()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_catalog():
    """Upload and process product catalog"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read the file based on extension
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            products = df.to_dict('records')
        elif file.filename.endswith('.json'):
            # Read JSON directly without pandas to avoid ordering issues
            import json as json_module
            file_content = file.read().decode('utf-8')
            products = json_module.loads(file_content)
            # Ensure it's a list
            if not isinstance(products, list):
                return jsonify({'error': 'JSON file must contain an array of products'}), 400
        else:
            return jsonify({'error': 'Unsupported file format. Use CSV or JSON'}), 400
        
        # Add products to vector store
        count = vector_store.add_products(products)
        
        return jsonify({
            'message': 'Catalog uploaded successfully',
            'products_count': count
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_products():
    """Query products using natural language"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get RAG response
        response = vector_store.query(query)
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products from vector store"""
    try:
        products = vector_store.get_all_products()
        return jsonify({'products': products}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear', methods=['DELETE'])
def clear_database():
    """Clear all products from vector store"""
    try:
        vector_store.clear()
        return jsonify({'message': 'Database cleared successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        stats = vector_store.get_stats()
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
