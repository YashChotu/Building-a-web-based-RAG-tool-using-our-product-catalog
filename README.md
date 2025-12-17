# Product Catalog RAG Application

A web-based Retrieval-Augmented Generation (RAG) tool for querying product catalogs using natural language.

## Features

- 🔍 **Semantic Search**: Find products using natural language queries
- 🤖 **AI-Powered Responses**: Get intelligent answers about your product catalog
- 📊 **Product Management**: Upload and manage product catalogs (CSV/JSON)
- 🌐 **Web Interface**: User-friendly interface for querying products
- 💾 **Vector Embeddings**: OpenAI embeddings for efficient semantic search

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment**
```bash
python -m venv venv
```

3. **Activate the virtual environment**
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## Usage

1. **Start the application**
```bash
python app.py
```

2. **Open your browser**
   - Navigate to `http://localhost:5000`

3. **Upload your product catalog**
   - Click "Upload Catalog" and select a CSV or JSON file
   - Sample data is provided in `sample_products.json`

4. **Query your products**
   - Ask natural language questions like:
     - "What laptops do you have under $1000?"
     - "Show me wireless headphones with noise cancellation"
     - "Which products are best for gaming?"

## API Endpoints

- `POST /api/upload` - Upload product catalog
- `POST /api/query` - Query products using natural language
- `GET /api/products` - Get all products
- `DELETE /api/clear` - Clear the vector database

## Project Structure

```
├── app.py                  # Flask application and API endpoints
├── vector_store.py         # Vector database and RAG logic
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Frontend logic
├── templates/
│   └── index.html         # Main web interface
├── sample_products.json   # Sample product data
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Technologies Used

- **Backend**: Flask, Python
- **Vector Database**: ChromaDB
- **LLM**: OpenAI GPT-4
- **Embeddings**: OpenAI text-embedding-3-small
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

## License

MIT
