"""
Chatbot RAG Routes
Handles chatbot functionality with RAG (Retrieval-Augmented Generation)
"""

from flask import Blueprint, request, jsonify
import mysql.connector
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)

# Lazy loading for heavy dependencies
_embedder = None
_llm_agent = None
_db_connection = None

# Configuration from environment or defaults
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma2:2b')

# TiDB Cloud Configuration (for RAG database)
RAG_DB_HOST = os.getenv('RAG_DB_HOST', 'gateway01.eu-central-1.prod.aws.tidbcloud.com')
RAG_DB_PORT = int(os.getenv('RAG_DB_PORT', 4000))
RAG_DB_USER = os.getenv('RAG_DB_USER', 'mi3fQyPy1G6E9Jx.root')
RAG_DB_PASSWORD = os.getenv('RAG_DB_PASSWORD', 'NKFZCVf7VuaM2WFv')
RAG_DB_NAME = os.getenv('RAG_DB_NAME', 'RAG')
RAG_SSL_CA = os.getenv('RAG_SSL_CA', os.path.join(os.path.dirname(__file__), '..', 'isrgrootx1.pem'))


def get_embedder():
    """Lazy load the sentence transformer embedder"""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer('BAAI/bge-m3')
            print("✅ Embedder loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load embedder: {e}")
            raise
    return _embedder


def get_llm_agent():
    """Lazy load the Ollama LLM client"""
    global _llm_agent
    if _llm_agent is None:
        try:
            import ollama
            _llm_agent = ollama.Client(host=OLLAMA_HOST)
            print(f"✅ LLM Agent connected to {OLLAMA_HOST}")
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            raise
    return _llm_agent


def get_rag_db():
    """Get or create RAG database connection"""
    global _db_connection
    try:
        # Check if connection exists and is still alive
        if _db_connection is not None:
            try:
                _db_connection.ping(reconnect=True, attempts=3, delay=2)
                return _db_connection
            except:
                _db_connection = None
        
        # Create new connection
        _db_connection = mysql.connector.connect(
            host=RAG_DB_HOST,
            port=RAG_DB_PORT,
            user=RAG_DB_USER,
            password=RAG_DB_PASSWORD,
            database=RAG_DB_NAME,
            ssl_ca=RAG_SSL_CA,
            ssl_verify_cert=True,
            ssl_verify_identity=True
        )
        print("✅ RAG Database connected successfully")
        return _db_connection
    except Exception as e:
        print(f"❌ Failed to connect to RAG database: {e}")
        raise


def search_document(database, query, k_top=5):
    """Search for relevant documents using vector similarity"""
    results = []
    try:
        embedder = get_embedder()
        query_embedding_list = embedder.encode(query).tolist()
        query_embedding_str = json.dumps(query_embedding_list)

        curr = database.cursor()

        sql_query = f"""
        SELECT text, vec_cosine_distance(embedding, %s) AS distance
        FROM documents
        ORDER BY distance ASC
        LIMIT {k_top}
        """

        curr.execute(sql_query, (query_embedding_str,))
        search_results = curr.fetchall()
        database.commit()
        curr.close()

        for result in search_results:
            text, distance = result
            results.append({"text": text, "distance": float(distance)})

        return results
    except Exception as e:
        print(f"❌ Error searching documents: {e}")
        raise


def generate_response(database, query):
    """Generate response using RAG (Retrieval-Augmented Generation)"""
    try:
        # Step 1: Retrieve relevant documents
        retrieved_docs = search_document(database, query)
        
        if not retrieved_docs:
            return "Maaf, saya tidak menemukan informasi yang relevan. Silakan coba pertanyaan lain."

        # Step 2: Build context from retrieved documents
        context = "\n".join([doc["text"] for doc in retrieved_docs])
        
        # Step 3: Create prompt with context
        prompt = f"""Anda adalah EcoBot, asisten virtual untuk aplikasi RuangHijau yang fokus pada lingkungan dan kelestarian alam.

Konteks informasi yang tersedia:
{context}

Berdasarkan konteks di atas, jawab pertanyaan berikut dengan ramah dan informatif dalam Bahasa Indonesia.
Jika informasi tidak ada dalam konteks, katakan bahwa Anda tidak memiliki informasi tersebut tetapi tetap bantu semampu Anda.

Pertanyaan: {query}

Jawaban:"""

        # Step 4: Generate response using LLM
        llm = get_llm_agent()
        response = llm.chat(
            model=OLLAMA_MODEL, 
            messages=[{"role": "user", "content": prompt}]
        )

        return response['message']['content']
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        raise


@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for the RAG chatbot
    
    Request JSON:
    {
        "message": "User's message here",
        "user_id": "optional_user_id"
    }
    
    Response JSON:
    {
        "success": true,
        "response": "Bot's response message",
        "user_id": "user_id if provided"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        print(f"📨 Chat request from {user_id}: {user_message[:50]}...")
        
        # Get database connection
        db = get_rag_db()
        
        # Generate response using RAG
        bot_response = generate_response(db, user_message)
        
        print(f"🤖 Bot response generated: {bot_response[:50]}...")
        
        return jsonify({
            "success": True,
            "response": bot_response,
            "user_id": user_id
        }), 200
        
    except mysql.connector.Error as db_err:
        print(f"❌ Database error: {db_err}")
        return jsonify({
            "success": False,
            "error": "Database connection error",
            "message": str(db_err)
        }), 503
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to process chat request",
            "message": str(e)
        }), 500


@chatbot_bp.route('/health', methods=['GET'])
def health_check():
    """Check if the chatbot service is healthy"""
    status = {
        "chatbot": "running",
        "embedder": "unknown",
        "llm": "unknown",
        "rag_database": "unknown"
    }
    
    try:
        # Test embedder
        get_embedder()
        status["embedder"] = "healthy"
    except Exception as e:
        status["embedder"] = f"error: {str(e)}"
    
    try:
        # Test LLM connection
        get_llm_agent()
        status["llm"] = "healthy"
    except Exception as e:
        status["llm"] = f"error: {str(e)}"
    
    try:
        # Test database connection
        db = get_rag_db()
        db.ping()
        status["rag_database"] = "healthy"
    except Exception as e:
        status["rag_database"] = f"error: {str(e)}"
    
    all_healthy = all(v == "healthy" for k, v in status.items() if k != "chatbot")
    
    return jsonify({
        "success": all_healthy,
        "status": status
    }), 200 if all_healthy else 503


@chatbot_bp.route('/search', methods=['POST'])
def search():
    """
    Search for relevant documents without generating a response
    Useful for debugging or showing sources
    
    Request JSON:
    {
        "query": "Search query here",
        "k_top": 5 (optional, default 5)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        query = data.get('query', '').strip()
        k_top = data.get('k_top', 5)
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400
        
        db = get_rag_db()
        results = search_document(db, query, k_top)
        
        return jsonify({
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }), 200
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to search documents",
            "message": str(e)
        }), 500
