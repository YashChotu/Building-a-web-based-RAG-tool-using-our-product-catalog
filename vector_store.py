from openai import OpenAI
import os
from typing import List, Dict
import json
import numpy as np

class VectorStore:
    def __init__(self):
        """Initialize OpenAI client and in-memory storage"""
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # In-memory storage for products and embeddings
        self.products = []
        self.embeddings = []
        self.ids = []
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}")
            raise
    
    def _product_to_text(self, product: Dict) -> str:
        """Convert product dictionary to searchable text"""
        text_parts = []
        
        # Add all product fields to the text representation
        for key, value in product.items():
            if value is not None and value != '':
                text_parts.append(f"{key}: {value}")
        
        return "\n".join(text_parts)
    
    def add_products(self, products: List[Dict]) -> int:
        """Add products to the vector store"""
        for idx, product in enumerate(products):
            # Create text representation
            text = self._product_to_text(product)
            
            # Create embedding
            embedding = self._create_embedding(text)
            
            # Store everything
            self.products.append(product)
            self.embeddings.append(embedding)
            
            # Create unique ID
            product_id = product.get('id', f"product_{idx}")
            self.ids.append(str(product_id))
        
        return len(products)
    
    def query(self, query_text: str, n_results: int = 5) -> Dict:
        """Query the vector store and generate response using RAG"""
        try:
            if not self.products:
                return {
                    'answer': "No products in database. Please upload a product catalog first.",
                    'products': [],
                    'count': 0
                }
            
            # Create query embedding
            query_embedding = self._create_embedding(query_text)
            
            # Calculate cosine similarities
            similarities = []
            for emb in self.embeddings:
                similarity = self._cosine_similarity(query_embedding, emb)
                similarities.append(similarity)
            
            # Get top N results
            top_indices = np.argsort(similarities)[-n_results:][::-1]
            relevant_products = [self.products[i] for i in top_indices]
            
            # Generate response using GPT
            if relevant_products:
                context = self._format_context(relevant_products)
                response_text = self._generate_response(query_text, context)
            else:
                response_text = "I couldn't find any products matching your query."
                relevant_products = []
            
            return {
                'answer': response_text,
                'products': relevant_products,
                'count': len(relevant_products)
            }
        
        except Exception as e:
            print(f"Error in query: {e}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def _format_context(self, products: List[Dict]) -> str:
        """Format products as context for the LLM"""
        context_parts = ["Here are the relevant products from the catalog:\n"]
        
        for idx, product in enumerate(products, 1):
            context_parts.append(f"\nProduct {idx}:")
            for key, value in product.items():
                context_parts.append(f"  {key}: {value}")
        
        return "\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str) -> str:
        """Generate response using OpenAI GPT"""
        try:
            system_prompt = """You are a helpful product catalog assistant. 
            Based on the product information provided, answer the user's question accurately and concisely.
            If asked for recommendations, suggest the most relevant products.
            Be friendly and informative."""
            
            user_prompt = f"""Context (Product Catalog):
{context}

User Question: {query}

Please provide a helpful answer based on the products above."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Found {len(context)} relevant products, but couldn't generate a detailed response."
    
    def get_all_products(self) -> List[Dict]:
        """Get all products from the vector store"""
        return self.products
    
    def clear(self):
        """Clear all products from the vector store"""
        self.products = []
        self.embeddings = []
        self.ids = []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            'total_products': len(self.products),
            'collection_name': 'in_memory_catalog'
        }
