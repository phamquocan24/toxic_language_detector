# # utils/vector_utils.py
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import re

# # Initialize the vectorizer
# _vectorizer = None

# def _get_vectorizer():
#     """
#     Get or initialize the TF-IDF vectorizer
#     """
#     global _vectorizer
#     if _vectorizer is None:
#         _vectorizer = TfidfVectorizer(
#             max_features=5000,
#             stop_words='english',
#             ngram_range=(1, 2)
#         )
#     return _vectorizer

# def preprocess_text(text):
#     """
#     Preprocess Vietnamese text for vectorization
    
#     Args:
#         text (str): Raw Vietnamese text
        
#     Returns:
#         str: Preprocessed text
#     """
#     # Convert to lowercase (preserving Vietnamese diacritical marks)
#     text = text.lower()
    
#     # Remove URLs
#     text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
#     # Remove HTML tags
#     text = re.sub(r'<.*?>', '', text)
    
#     # For Vietnamese text, we need to preserve diacritical marks
#     # Only remove punctuation that doesn't affect meaning
#     text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)
#     text = re.sub(r'\d+', '', text)
    
#     # Remove extra whitespace
#     text = re.sub(r'\s+', ' ', text).strip()
    
#     # Use Vietnamese-specific tokenization if available
#     try:
#         from underthesea import word_tokenize
#         text = word_tokenize(text, format="text")
#     except ImportError:
#         # Fallback if underthesea is not available
#         pass
    
#     return text

# def extract_features(text):
#     """
#     Extract feature vector from text
    
#     Args:
#         text (str): Input text
        
#     Returns:
#         numpy.ndarray: Feature vector
#     """
#     # Get vectorizer
#     vectorizer = _get_vectorizer()
    
#     # Preprocess text
#     processed_text = preprocess_text(text)
    
#     # Fit vectorizer if not trained
#     if not hasattr(vectorizer, 'vocabulary_'):
#         vectorizer.fit([processed_text])
    
#     # Transform text to vector
#     vector = vectorizer.transform([processed_text])
    
#     # Return as dense array
#     return vector.toarray()[0]

# def compute_similarity(vec1, vec2):
#     """
#     Compute cosine similarity between two vectors
    
#     Args:
#         vec1 (numpy.ndarray): First vector
#         vec2 (numpy.ndarray): Second vector
        
#     Returns:
#         float: Similarity score (0-1)
#     """
#     # Reshape vectors if needed
#     if len(vec1.shape) == 1:
#         vec1 = vec1.reshape(1, -1)
#     if len(vec2.shape) == 1:
#         vec2 = vec2.reshape(1, -1)
    
#     # Compute similarity
#     sim = cosine_similarity(vec1, vec2)[0][0]
    
#     return float(sim)

# def find_similar_vectors(query_vector, vectors, threshold=0.7, top_n=10):
#     """
#     Find similar vectors to a query vector
    
#     Args:
#         query_vector (numpy.ndarray): Query vector
#         vectors (List[numpy.ndarray]): List of vectors to compare against
#         threshold (float): Minimum similarity threshold
#         top_n (int): Maximum number of results to return
        
#     Returns:
#         List[Tuple[int, float]]: List of (index, similarity) tuples
#     """
#     similarities = []
    
#     for i, vec in enumerate(vectors):
#         sim = compute_similarity(query_vector, vec)
#         if sim >= threshold:
#             similarities.append((i, sim))
    
#     # Sort by similarity (descending)
#     similarities.sort(key=lambda x: x[1], reverse=True)
    
#     # Return top N results
#     return similarities[:top_n]
# utils/vector_utils.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import re
import os
import pickle
import logging
from typing import List, Tuple, Dict, Any, Optional, Union
import joblib
from backend.config.settings import settings

# Thiết lập logging
logger = logging.getLogger("utils.vector_utils")

# Khởi tạo vectorizer
_vectorizer = None
_svd = None
_vietnamese_stopwords = None

def _get_vietnamese_stopwords() -> List[str]:
    """
    Lấy danh sách stopwords tiếng Việt
    
    Returns:
        List[str]: Danh sách stopwords tiếng Việt
    """
    global _vietnamese_stopwords
    
    if _vietnamese_stopwords is not None:
        return _vietnamese_stopwords
    
    # Tìm file stopwords tiếng Việt
    stopwords_path = getattr(settings, 'VIETNAMESE_STOPWORDS_FILE', None)
    
    if stopwords_path and os.path.exists(stopwords_path):
        try:
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                _vietnamese_stopwords = [line.strip() for line in f if line.strip()]
                logger.info(f"Đã tải {len(_vietnamese_stopwords)} stopwords từ {stopwords_path}")
        except Exception as e:
            logger.error(f"Lỗi khi tải stopwords: {str(e)}")
            _vietnamese_stopwords = []
    else:
        # Stopwords tiếng Việt mặc định
        _vietnamese_stopwords = [
            'và', 'của', 'cho', 'là', 'đến', 'trong', 'với', 'các', 'có', 'được', 'tại', 'về',
            'những', 'như', 'không', 'này', 'từ', 'theo', 'trên', 'cũng', 'đã', 'sẽ', 'vì', 'nhưng',
            'ra', 'còn', 'bị', 'đó', 'để', 'nên', 'khi', 'một', 'mà', 'do', 'đề', 'thì', 'phải',
            'qua', 'đi', 'nếu', 'làm', 'mới', 'vào', 'hay', 'rằng', 'bởi', 'vậy', 'sau', 'rất',
            'mình', 'chỉ', 'thế', 'tôi', 'anh', 'chị', 'bạn', 'họ', 'nhiều', 'đâu', 'thêm', 'à', 'vâng'
        ]
        logger.info(f"Sử dụng {len(_vietnamese_stopwords)} stopwords mặc định tiếng Việt")
    
    return _vietnamese_stopwords

def _get_vectorizer(force_new: bool = False) -> TfidfVectorizer:
    """
    Lấy hoặc khởi tạo TF-IDF vectorizer
    
    Args:
        force_new: Có tạo mới vectorizer không
        
    Returns:
        TfidfVectorizer: TF-IDF vectorizer
    """
    global _vectorizer
    
    if _vectorizer is None or force_new:
        # Lấy stopwords tiếng Việt
        stopwords = _get_vietnamese_stopwords()
        
        # Khởi tạo vectorizer mới
        _vectorizer = TfidfVectorizer(
            max_features=10000,  # Tăng số lượng đặc trưng để hỗ trợ tiếng Việt tốt hơn
            stop_words=stopwords,
            ngram_range=(1, 2),  # Sử dụng cả unigram và bigram
            min_df=1,            # Chấp nhận các từ xuất hiện ít nhất 1 lần (cho phép xử lý văn bản ngắn)
            max_df=0.95,         # Bỏ qua các từ quá phổ biến
            use_idf=True,        # Sử dụng idf
            norm='l2',           # Chuẩn hóa L2
            smooth_idf=True,     # Làm mịn idf
            sublinear_tf=True,   # Áp dụng log-scaling cho tf
            lowercase=True,      # Chuyển đổi text thành chữ thường
            analyzer='word',     # Phân tích theo từ (thay vì ký tự)
            token_pattern=r'(?u)\b\w\w+\b|[^\s]+'  # Pattern mở rộng để bao gồm ký tự tiếng Việt
        )
        
        logger.info("Đã khởi tạo TF-IDF vectorizer mới")
    
    return _vectorizer

def _get_svd_reducer(n_components: int = 300, force_new: bool = False) -> TruncatedSVD:
    """
    Lấy hoặc khởi tạo SVD reducer để giảm chiều vector
    
    Args:
        n_components: Số chiều sau khi giảm
        force_new: Có tạo mới reducer không
        
    Returns:
        TruncatedSVD: SVD reducer
    """
    global _svd
    
    if _svd is None or force_new:
        _svd = TruncatedSVD(n_components=n_components, random_state=42)
        logger.info(f"Đã khởi tạo SVD reducer mới với {n_components} chiều")
    
    return _svd

def load_vectorizer(filepath: str) -> bool:
    """
    Tải vectorizer đã được huấn luyện từ file
    
    Args:
        filepath: Đường dẫn đến file vectorizer
        
    Returns:
        bool: True nếu tải thành công, False nếu không
    """
    global _vectorizer
    
    try:
        _vectorizer = joblib.load(filepath)
        logger.info(f"Đã tải vectorizer từ {filepath}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi tải vectorizer từ {filepath}: {str(e)}")
        # Fallback về vectorizer mới
        _vectorizer = _get_vectorizer(force_new=True)
        return False

def save_vectorizer(filepath: str) -> bool:
    """
    Lưu vectorizer hiện tại vào file
    
    Args:
        filepath: Đường dẫn đến file
        
    Returns:
        bool: True nếu lưu thành công, False nếu không
    """
    global _vectorizer
    
    if _vectorizer is None:
        logger.error("Không có vectorizer để lưu")
        return False
    
    try:
        joblib.dump(_vectorizer, filepath)
        logger.info(f"Đã lưu vectorizer vào {filepath}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu vectorizer vào {filepath}: {str(e)}")
        return False

def preprocess_text(text: str) -> str:
    """
    Tiền xử lý văn bản tiếng Việt để vector hóa
    
    Args:
        text: Văn bản tiếng Việt thô
        
    Returns:
        str: Văn bản đã tiền xử lý
    """
    if not text:
        return ""
    
    # Chuyển thành chữ thường (giữ nguyên dấu tiếng Việt)
    text = text.lower()
    
    # Loại bỏ URL
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Loại bỏ HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Với tiếng Việt, chúng ta cần giữ nguyên dấu
    # Chỉ loại bỏ dấu câu không ảnh hưởng đến ý nghĩa
    text = re.sub(r'[.,;:!?()"\'\[\]/\\]', ' ', text)
    
    # Loại bỏ số
    text = re.sub(r'\d+', '', text)
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Sử dụng tokenize tiếng Việt nếu có
    try:
        from underthesea import word_tokenize
        text = word_tokenize(text, format="text")
        logger.debug("Đã sử dụng underthesea để tokenize tiếng Việt")
    except ImportError:
        # Fallback nếu không có underthesea
        logger.debug("Không thể sử dụng underthesea, fallback về tokenize mặc định")
        pass
    
    return text

def extract_features(text: str, reduce_dim: bool = False) -> np.ndarray:
    """
    Trích xuất vector đặc trưng từ văn bản
    
    Args:
        text: Văn bản đầu vào
        reduce_dim: Có giảm chiều vector không
        
    Returns:
        np.ndarray: Vector đặc trưng
    """
    if not text:
        if reduce_dim:
            n_components = _get_svd_reducer().n_components
            return np.zeros(n_components)
        else:
            return np.array([])
    
    # Lấy vectorizer
    vectorizer = _get_vectorizer()
    
    # Tiền xử lý văn bản
    processed_text = preprocess_text(text)
    
    if not processed_text.strip():
        return np.zeros(10000)

    try:
#        vector = vectorizer.fit_transform([processed_text]).toarray()[0]
        # Thay vì fit_transform, chỉ sử dụng transform
        # Nếu vectorizer chưa được fit, hãy trả về vector 0
        if not hasattr(vectorizer, 'vocabulary_'):
            logger.warning("Vectorizer chưa được huấn luyện, sử dụng vector 0")
            return np.zeros(10000)
            
        vector = vectorizer.transform([processed_text]).toarray()[0]
    except ValueError as e:
        logging.error("Error in vectorizer.fit_transform: %s. Returning zero vector.", e)
        vector = np.zeros(10000)
    
    # Giảm chiều nếu được yêu cầu
    if reduce_dim:
        svd = _get_svd_reducer()
        if not hasattr(svd, 'components_'):
            logger.warning("SVD chưa được huấn luyện, không thể giảm chiều vector")
            # Trả về vector đặc mật (sparse) dưới dạng mảng đặc (dense)
            return vector
        
        reduced_vector = svd.transform(vector.reshape(1, -1))
        return reduced_vector[0]
    
    # Trả về vector dưới dạng mảng đặc (dense)
    return vector

def compute_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Tính độ tương tự cosine giữa hai vector
    
    Args:
        vec1: Vector thứ nhất
        vec2: Vector thứ hai
        
    Returns:
        float: Điểm tương tự (0-1)
    """
    if vec1 is None or vec2 is None:
        return 0.0
    
    if len(vec1) == 0 or len(vec2) == 0:
        return 0.0
    
    # Reshape vectors nếu cần
    if len(vec1.shape) == 1:
        vec1 = vec1.reshape(1, -1)
    if len(vec2.shape) == 1:
        vec2 = vec2.reshape(1, -1)
    
    # Kiểm tra kích thước
    if vec1.shape[1] != vec2.shape[1]:
        logger.warning(f"Không thể tính cosine similarity: Kích thước vector không khớp ({vec1.shape[1]} vs {vec2.shape[1]})")
        # Có thể fallback về padding hoặc truncating, nhưng tốt nhất là báo lỗi
        return 0.0
    
    # Tính độ tương tự
    sim = cosine_similarity(vec1, vec2)[0][0]
    
    return float(sim)

def find_similar_vectors(query_vector: np.ndarray, vectors: List[np.ndarray], 
                         threshold: float = 0.7, top_n: int = 10) -> List[Tuple[int, float]]:
    """
    Tìm các vector tương tự với vector truy vấn
    
    Args:
        query_vector: Vector truy vấn
        vectors: Danh sách vector để so sánh
        threshold: Ngưỡng tương tự tối thiểu
        top_n: Số lượng kết quả tối đa trả về
        
    Returns:
        List[Tuple[int, float]]: Danh sách các tuple (index, độ tương tự)
    """
    if query_vector is None or len(vectors) == 0:
        return []
    
    # Reshape query vector
    if len(query_vector.shape) == 1:
        query_vector = query_vector.reshape(1, -1)
    
    similarities = []
    
    for i, vec in enumerate(vectors):
        if vec is None or len(vec) == 0:
            continue
            
        # Reshape vector
        if len(vec.shape) == 1:
            vec = vec.reshape(1, -1)
        
        # Kiểm tra kích thước
        if vec.shape[1] != query_vector.shape[1]:
            logger.warning(f"Bỏ qua vector {i}: Kích thước không khớp ({vec.shape[1]} vs {query_vector.shape[1]})")
            continue
        
        # Tính độ tương tự
        sim = compute_similarity(query_vector, vec)
        
        if sim >= threshold:
            similarities.append((i, float(sim)))
    
    # Sắp xếp theo độ tương tự (giảm dần)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Trả về top N kết quả
    return similarities[:top_n]

def batch_compute_similarity(query_vector: np.ndarray, vectors: List[np.ndarray], 
                            threshold: float = 0.0) -> List[Tuple[int, float]]:
    """
    Tính độ tương tự hàng loạt giữa một vector truy vấn và nhiều vector khác
    
    Args:
        query_vector: Vector truy vấn
        vectors: Danh sách vector để so sánh
        threshold: Ngưỡng tương tự tối thiểu
        
    Returns:
        List[Tuple[int, float]]: Danh sách các tuple (index, độ tương tự)
    """
    if query_vector is None or len(vectors) == 0:
        return []
    
    # Reshape query vector
    if len(query_vector.shape) == 1:
        query_vector = query_vector.reshape(1, -1)
    
    # Lọc các vector có cùng kích thước với query_vector
    valid_vectors = []
    valid_indices = []
    
    for i, vec in enumerate(vectors):
        if vec is None or len(vec) == 0:
            continue
            
        # Reshape vector
        if len(vec.shape) == 1:
            vec = vec.reshape(1, -1)
        
        # Kiểm tra kích thước
        if vec.shape[1] == query_vector.shape[1]:
            valid_vectors.append(vec)
            valid_indices.append(i)
    
    if not valid_vectors:
        return []
    
    # Ghép các vector lại thành một ma trận
    matrix = np.vstack(valid_vectors)
    
    # Tính độ tương tự hàng loạt
    similarities = cosine_similarity(query_vector, matrix)[0]
    
    # Lọc các kết quả trên ngưỡng
    results = [(valid_indices[i], float(sim)) for i, sim in enumerate(similarities) if sim >= threshold]
    
    # Sắp xếp theo độ tương tự (giảm dần)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results

def train_vectorizer_on_corpus(corpus: List[str], max_features: int = 10000, 
                              save_path: Optional[str] = None) -> TfidfVectorizer:
    """
    Huấn luyện vectorizer trên một tập văn bản
    
    Args:
        corpus: Danh sách các văn bản
        max_features: Số lượng đặc trưng tối đa
        save_path: Đường dẫn để lưu vectorizer (nếu có)
        
    Returns:
        TfidfVectorizer: Vectorizer đã huấn luyện
    """
    if not corpus:
        logger.error("Không thể huấn luyện vectorizer: Corpus rỗng")
        return _get_vectorizer()
    
    # Tiền xử lý corpus
    processed_corpus = [preprocess_text(text) for text in corpus]
    
    # Lấy vectorizer mới
    vectorizer = _get_vectorizer(force_new=True)
    
    # Cập nhật max_features
    vectorizer.max_features = max_features
    
    # Huấn luyện vectorizer
    vectorizer.fit(processed_corpus)
    
    logger.info(f"Đã huấn luyện vectorizer trên {len(corpus)} văn bản với {len(vectorizer.vocabulary_)} đặc trưng")
    
    # Lưu vectorizer nếu có đường dẫn
    if save_path:
        save_vectorizer(save_path)
    
    global _vectorizer
    _vectorizer = vectorizer
    
    return vectorizer

def train_svd_on_corpus(corpus: List[str], n_components: int = 300, 
                       save_path: Optional[str] = None) -> TruncatedSVD:
    """
    Huấn luyện SVD reducer trên một tập văn bản
    
    Args:
        corpus: Danh sách các văn bản
        n_components: Số chiều sau khi giảm
        save_path: Đường dẫn để lưu SVD reducer (nếu có)
        
    Returns:
        TruncatedSVD: SVD reducer đã huấn luyện
    """
    if not corpus:
        logger.error("Không thể huấn luyện SVD: Corpus rỗng")
        return _get_svd_reducer()
    
    # Tiền xử lý corpus
    processed_corpus = [preprocess_text(text) for text in corpus]
    
    # Lấy vectorizer
    vectorizer = _get_vectorizer()
    
    # Chuyển đổi corpus thành ma trận TF-IDF
    tfidf_matrix = vectorizer.transform(processed_corpus)
    
    # Lấy SVD reducer mới
    svd = _get_svd_reducer(n_components=n_components, force_new=True)
    
    # Huấn luyện SVD
    svd.fit(tfidf_matrix)
    
    logger.info(f"Đã huấn luyện SVD reducer trên {len(corpus)} văn bản với {n_components} chiều")
    
    # Lưu SVD nếu có đường dẫn
    if save_path:
        try:
            joblib.dump(svd, save_path)
            logger.info(f"Đã lưu SVD reducer vào {save_path}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu SVD reducer vào {save_path}: {str(e)}")
    
    global _svd
    _svd = svd
    
    return svd