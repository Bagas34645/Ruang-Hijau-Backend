from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np
from io import BytesIO
import base64

# Try to import ML dependencies
try:
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
    from tensorflow.keras.preprocessing import image as keras_image
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False
    print("⚠️ TensorFlow/Keras not available, using fallback detection")

waste_detection_bp = Blueprint('waste_detection', __name__)

# Klasifikasi sampah berdasarkan jenis
WASTE_CATEGORIES = {
    'organik': {
        'bin_color': 'Hijau',
        'bin_code': 'GRN',
        'examples': ['sisa makanan', 'kulit buah', 'daun', 'sayuran busuk', 'tulang ikan', 'cangkang telur'],
        'keywords': ['banana', 'apple', 'orange', 'vegetable', 'fruit', 'food', 'meat', 'fish', 'egg', 'leaf', 'plant'],
        'description': 'Sampah yang dapat terurai secara alami',
        'icon': '🟢'
    },
    'anorganik': {
        'bin_color': 'Kuning',
        'bin_code': 'YEL',
        'examples': ['plastik', 'botol plastik', 'kantong plastik', 'styrofoam', 'sedotan'],
        'keywords': ['plastic', 'bottle', 'bag', 'container', 'cup', 'straw', 'packaging', 'foam'],
        'description': 'Sampah yang sulit terurai dan dapat didaur ulang',
        'icon': '🟡'
    },
    'kertas': {
        'bin_color': 'Biru',
        'bin_code': 'BLU',
        'examples': ['kertas', 'kardus', 'koran', 'majalah', 'karton'],
        'keywords': ['paper', 'cardboard', 'newspaper', 'magazine', 'box', 'book', 'envelope'],
        'description': 'Sampah berbahan kertas yang dapat didaur ulang',
        'icon': '🔵'
    },
    'kaca': {
        'bin_color': 'Putih',
        'bin_code': 'WHT',
        'examples': ['botol kaca', 'gelas kaca', 'pecahan kaca', 'toples kaca'],
        'keywords': ['glass', 'bottle', 'jar', 'mirror', 'window'],
        'description': 'Sampah berbahan kaca yang dapat didaur ulang',
        'icon': '⚪'
    },
    'logam': {
        'bin_color': 'Abu-abu',
        'bin_code': 'GRY',
        'examples': ['kaleng', 'besi', 'aluminium', 'kawat', 'paku'],
        'keywords': ['can', 'metal', 'aluminum', 'steel', 'iron', 'wire', 'tin'],
        'description': 'Sampah berbahan logam yang dapat didaur ulang',
        'icon': '⚫'
    },
    'b3': {
        'bin_color': 'Merah',
        'bin_code': 'RED',
        'examples': ['baterai', 'lampu', 'obat kadaluarsa', 'pestisida', 'cat'],
        'keywords': ['battery', 'bulb', 'lamp', 'medicine', 'chemical', 'paint'],
        'description': 'Sampah Bahan Berbahaya dan Beracun (B3) yang memerlukan penanganan khusus',
        'icon': '🔴'
    }
}

# Global model (lazy loading)
_model = None

def get_model():
    """Load model once and reuse"""
    global _model
    if ML_AVAILABLE and _model is None:
        try:
            _model = MobileNetV2(weights='imagenet', include_top=True)
            print("✅ ML Model loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load ML model: {e}")
            _model = False
    return _model if ML_AVAILABLE and _model else None

def predict_with_ml(img_path):
    """
    Prediksi menggunakan MobileNetV2 + mapping ke kategori sampah
    """
    model = get_model()
    if model is None:
        return None
    
    try:
        # Load dan preprocess gambar
        img = keras_image.load_img(img_path, target_size=(224, 224))
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Prediksi
        predictions = model.predict(img_array, verbose=0)
        decoded = decode_predictions(predictions, top=5)[0]
        
        # Mapping prediksi ke kategori sampah
        for pred in decoded:
            class_name = pred[1].lower()
            confidence = float(pred[2])
            
            # Cek setiap kategori sampah
            for category, data in WASTE_CATEGORIES.items():
                for keyword in data['keywords']:
                    if keyword in class_name:
                        return {
                            'category': category,
                            'confidence': confidence,
                            'detected_object': pred[1],
                            'method': 'ml'
                        }
        
        # Jika tidak match, kembalikan None untuk fallback
        return None
        
    except Exception as e:
        print(f"Error dalam ML prediction: {e}")
        return None

def detect_waste_fallback(filename):
    """
    Fallback detection berdasarkan nama file
    """
    filename_lower = filename.lower()
    
    for category, data in WASTE_CATEGORIES.items():
        for example in data['examples']:
            if example.replace(' ', '') in filename_lower.replace(' ', ''):
                return {
                    'category': category,
                    'confidence': 0.75,
                    'detected_object': example,
                    'method': 'keyword'
                }
    
    return {
        'category': 'anorganik',
        'confidence': 0.5,
        'detected_object': 'unknown',
        'method': 'default'
    }

def analyze_image_color(img_path):
    """
    Analisis warna dominan dalam gambar untuk meningkatkan akurasi
    """
    try:
        img = Image.open(img_path)
        img = img.resize((150, 150))
        img_array = np.array(img)
        
        # Hitung warna dominan
        avg_color = img_array.mean(axis=(0, 1))
        
        return {
            'r': int(avg_color[0]) if len(avg_color) > 0 else 0,
            'g': int(avg_color[1]) if len(avg_color) > 1 else 0,
            'b': int(avg_color[2]) if len(avg_color) > 2 else 0
        }
    except:
        return {'r': 128, 'g': 128, 'b': 128}

@waste_detection_bp.route('/detect', methods=['POST'])
def detect_waste():
    """
    Deteksi jenis sampah dari gambar
    Menerima: POST /api/waste/detect
    - File: gambar sampah (form-data: file)
    - Returns: JSON dengan kategori, confidence, dan informasi sampah
    """
    try:
        # Cek jika file ada
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Tidak ada file yang diunggah'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'File tidak dipilih'
            }), 400
        
        # Cek tipe file
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                'success': False,
                'message': 'Format file tidak didukung. Gunakan: PNG, JPG, JPEG, GIF, BMP'
            }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], f"waste_{filename}")
        file.save(filepath)
        
        # Coba ML detection terlebih dahulu
        result = predict_with_ml(filepath)
        
        # Jika ML detection gagal, gunakan fallback
        if result is None:
            result = detect_waste_fallback(filename)
        
        # Analisis warna
        color_analysis = analyze_image_color(filepath)
        
        # Dapatkan informasi kategori
        category_info = WASTE_CATEGORIES.get(result['category'], {})
        
        # Construct response
        response = {
            'success': True,
            'detection': {
                'category': result['category'],
                'confidence': result['confidence'],
                'detected_object': result['detected_object'],
                'method': result['method']
            },
            'classification': {
                'bin_color': category_info.get('bin_color', ''),
                'bin_code': category_info.get('bin_code', ''),
                'description': category_info.get('description', ''),
                'icon': category_info.get('icon', '')
            },
            'color_analysis': color_analysis,
            'file': {
                'name': filename,
                'path': f"/uploads/waste_{filename}"
            }
        }
        
        # Clean up temporary file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Error in detect_waste: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@waste_detection_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get semua kategori sampah yang tersedia
    """
    try:
        categories_list = []
        for key, data in WASTE_CATEGORIES.items():
            categories_list.append({
                'id': key,
                'name': key.upper(),
                'bin_color': data['bin_color'],
                'bin_code': data['bin_code'],
                'icon': data['icon'],
                'description': data['description'],
                'examples': data['examples']
            })
        
        return jsonify({
            'success': True,
            'categories': categories_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@waste_detection_bp.route('/info', methods=['GET'])
def waste_info():
    """
    Get informasi singkat tentang waste detection API
    """
    return jsonify({
        'success': True,
        'info': {
            'name': 'Waste Detection API',
            'version': '1.0.0',
            'description': 'AI-powered waste classification system',
            'ml_available': ML_AVAILABLE,
            'supported_formats': ['PNG', 'JPG', 'JPEG', 'GIF', 'BMP'],
            'max_file_size': '16MB',
            'endpoints': {
                'detect': 'POST /api/waste/detect',
                'categories': 'GET /api/waste/categories',
                'info': 'GET /api/waste/info'
            }
        }
    }), 200
