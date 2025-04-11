# # utils/text_processing.py
# import re
# import urllib.parse

# def preprocess_for_spam_detection(text):
#     """
#     Tiền xử lý đặc biệt cho việc phát hiện spam
#     """
#     # Bản sao văn bản gốc để phân tích
#     original_text = text
    
#     # Xử lý các URL
#     # Tìm tất cả các URL trong văn bản
#     url_pattern = r'https?://\S+|www\.\S+|bit\.ly/\S+|goo\.gl/\S+|t\.co/\S+|tinyurl\.com/\S+'
#     urls = re.findall(url_pattern, original_text)
    
#     # Đánh dấu có URL
#     has_url = len(urls) > 0
    
#     # Đếm số lượng URL
#     url_count = len(urls)
    
#     # Kiểm tra các domain phổ biến trong spam
#     suspicious_domains = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'shorturl']
#     has_suspicious_url = any(domain in url for url in urls for domain in suspicious_domains)
    
#     # Xử lý các từ khóa spam tiếng Việt phổ biến
#     spam_keywords = [
#         'giảm giá', 'khuyến mãi', 'siêu sale', 'mua ngay', 'giá sốc', 'giá rẻ',
#         'liên hệ ngay', 'số lượng có hạn', 'cơ hội cuối', 'miễn phí', 'làm giàu',
#         'kiếm tiền tại nhà', 'thu nhập thụ động', 'việc làm thêm', 'đầu tư',
#         'chiết khấu', 'sale off', 'freeship', 'mua 1 tặng 1'
#     ]
    
#     # Chuẩn hóa văn bản để kiểm tra từ khóa
#     normalized_text = text.lower()
#     # Loại bỏ các ký tự đặc biệt thường dùng để tránh bộ lọc
#     normalized_text = re.sub(r'[._\-\s*]', '', normalized_text)
    
#     # Đếm số từ khóa spam xuất hiện
#     spam_keyword_count = sum(1 for keyword in spam_keywords if keyword.replace(' ', '') in normalized_text)
    
#     # Kiểm tra các đặc điểm đặc trưng của spam
#     has_excessive_punctuation = len(re.findall(r'[!?.]', text)) > 3
#     has_all_caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text)) > 0
    
#     # Tạo đặc trưng bổ sung cho mô hình
#     spam_features = {
#         'has_url': has_url,
#         'url_count': url_count,
#         'has_suspicious_url': has_suspicious_url,
#         'spam_keyword_count': spam_keyword_count,
#         'has_excessive_punctuation': has_excessive_punctuation,
#         'has_all_caps_words': has_all_caps_words
#     }
    
#     return text, spam_features
# utils/text_processing.py
import re
import urllib.parse
import string
import logging
import unicodedata
from typing import Dict, Any, List, Tuple, Optional
import json
from collections import Counter

# Thiết lập logging
logger = logging.getLogger("utils.text_processing")

def preprocess_text(text: str) -> str:
    """
    Tiền xử lý văn bản tiếng Việt cho dự đoán
    
    Args:
        text: Văn bản cần xử lý
        
    Returns:
        str: Văn bản đã xử lý
    """
    if not text:
        return ""
    
    # Loại bỏ URL
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    # Thay thế các ký tự đặc biệt bằng khoảng trắng
    text = re.sub(r'[^\w\s\d_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ]', ' ', text)
    
    # Chuẩn hóa dấu cách
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Chuyển thành chữ thường
    text = text.lower()
    
    return text

def remove_diacritics(text: str) -> str:
    """
    Loại bỏ dấu tiếng Việt
    
    Args:
        text: Văn bản cần xử lý
        
    Returns:
        str: Văn bản không dấu
    """
    return ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(c))

def preprocess_for_spam_detection(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Tiền xử lý đặc biệt cho việc phát hiện spam
    
    Args:
        text: Văn bản cần phân tích
        
    Returns:
        Tuple[str, Dict[str, Any]]: (Văn bản đã xử lý, đặc trưng spam)
    """
    if not text:
        return "", {
            'has_url': False,
            'url_count': 0,
            'has_suspicious_url': False,
            'spam_keyword_count': 0,
            'has_excessive_punctuation': False,
            'has_all_caps_words': False,
            'has_phone_number': False,
            'has_price': False,
            'has_suspicious_patterns': False,
            'emoji_count': 0,
            'capitalization_ratio': 0.0
        }
    
    # Bản sao văn bản gốc để phân tích
    original_text = text
    
    # Xử lý các URL
    # Tìm tất cả các URL trong văn bản
    url_pattern = r'https?://\S+|www\.\S+|bit\.ly/\S+|goo\.gl/\S+|t\.co/\S+|tinyurl\.com/\S+|fb\.me/\S+'
    urls = re.findall(url_pattern, original_text)
    
    # Đánh dấu có URL
    has_url = len(urls) > 0
    
    # Đếm số lượng URL
    url_count = len(urls)
    
    # Kiểm tra các domain đáng ngờ trong spam
    suspicious_domains = [
        'bit.ly', 'goo.gl', 'tinyurl.com', 't.co', 'shorturl', 'tiny.cc', 'fb.me',
        'clck.ru', 'ow.ly', 'j.mp', 'is.gd', 'rebrand.ly', 'soo.gd', 'x.co', 'tiny.ie'
    ]
    has_suspicious_url = any(domain in url.lower() for url in urls for domain in suspicious_domains)
    
    # Xử lý các từ khóa spam tiếng Việt phổ biến
    spam_keywords = [
        'giảm giá', 'khuyến mãi', 'siêu sale', 'mua ngay', 'giá sốc', 'giá rẻ', 'rẻ vô địch',
        'liên hệ ngay', 'số lượng có hạn', 'cơ hội cuối', 'miễn phí', 'làm giàu', 'hot', 'sốc',
        'kiếm tiền tại nhà', 'thu nhập thụ động', 'việc làm thêm', 'đầu tư', 'lợi nhuận cao',
        'chiết khấu', 'sale off', 'freeship', 'mua 1 tặng 1', 'chỉ hôm nay', 'click ngay',
        'cơ hội vàng', 'trúng thưởng', 'quà tặng', 'tri ân', 'ưu đãi', 'chỉ còn', 'trả góp',
        'không lãi suất', 'săn sale', 'flash sale', 'đồng giá', 'thanh lý', 'mua sỉ', 'giao hàng',
        'zalo', 'inbox', 'nhắn tin', 'liên hệ', 'hotline', 'bảo hành', 'đặt hàng', 'nhận chiết khấu'
    ]
    
    # Chuẩn hóa văn bản để kiểm tra từ khóa
    normalized_text = text.lower()
    # Loại bỏ dấu câu
    normalized_text = re.sub(r'[^\w\sÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ]', ' ', normalized_text)
    
    # Đếm số từ khóa spam xuất hiện
    spam_keyword_count = 0
    for keyword in spam_keywords:
        if keyword.lower() in normalized_text:
            spam_keyword_count += 1
    
    # Kiểm tra số điện thoại
    phone_pattern = r'(0|\+84)\s*\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{3,4}'
    has_phone_number = bool(re.search(phone_pattern, original_text))
    
    # Kiểm tra giá tiền
    price_pattern = r'\d+[.,]?\d*\s*([kK]|[đÐ]|VND|VNĐ|nghìn|triệu|[tT][rR])'
    has_price = bool(re.search(price_pattern, original_text))
    
    # Đếm emoji
    emoji_pattern = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+"
    )
    emojis = emoji_pattern.findall(original_text)
    emoji_count = len(emojis)
    
    # Kiểm tra các đặc điểm đặc trưng của spam
    has_excessive_punctuation = len(re.findall(r'[!?.]', text)) > 5
    has_all_caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text)) > 1
    
    # Tỷ lệ chữ hoa
    if len(text) > 0:
        upper_chars = sum(1 for c in text if c.isupper())
        capitalization_ratio = upper_chars / len(text)
    else:
        capitalization_ratio = 0
    
    # Các mẫu đáng ngờ
    suspicious_patterns = [
        r'\d+\s*%', # Phần trăm
        r'[cC][òoÒO][nN]\s*[íiÍI][tT]', # "còn ít" - dùng để tạo cảm giác khan hiếm
        r'[hH][êeÊE][tT]\s*[hH][àaÀA][nN][gG]', # "hết hàng"
        r'[mM][uU][aA]\s*[nN][gG][aA][yY]', # "mua ngay"
        r'[lL][iI][êeÊE][nN]\s*[hH][eêÊE]', # "liên hệ"
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' # Email
    ]
    
    has_suspicious_patterns = any(bool(re.search(pattern, text)) for pattern in suspicious_patterns)
    
    # Tạo đặc trưng bổ sung cho mô hình
    spam_features = {
        'has_url': has_url,
        'url_count': url_count,
        'has_suspicious_url': has_suspicious_url,
        'spam_keyword_count': spam_keyword_count,
        'has_excessive_punctuation': has_excessive_punctuation,
        'has_all_caps_words': has_all_caps_words,
        'has_phone_number': has_phone_number,
        'has_price': has_price,
        'has_suspicious_patterns': has_suspicious_patterns,
        'emoji_count': emoji_count,
        'capitalization_ratio': capitalization_ratio
    }
    
    return text, spam_features

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Trích xuất từ khóa từ văn bản
    
    Args:
        text: Văn bản cần trích xuất
        top_n: Số lượng từ khóa tối đa cần trích xuất
        
    Returns:
        List[str]: Danh sách từ khóa
    """
    if not text:
        return []
    
    # Tải danh sách stopwords từ file nếu có
    try:
        with open('data/vietnamese_stopwords.txt', 'r', encoding='utf-8') as f:
            stopwords = set(line.strip() for line in f)
    except:
        # Stopwords mặc định tiếng Việt nếu file không tồn tại
        stopwords = {
            'và', 'của', 'cho', 'là', 'đến', 'trong', 'với', 'các', 'có', 'được', 'tại', 'về',
            'những', 'như', 'không', 'này', 'từ', 'theo', 'trên', 'cũng', 'đã', 'sẽ', 'vì', 'nhưng',
            'ra', 'còn', 'bị', 'đó', 'để', 'nên', 'khi', 'một', 'mà', 'do', 'đề', 'thì', 'phải',
            'qua', 'đi', 'nếu', 'làm', 'mới', 'vào', 'hay', 'rằng', 'bởi', 'vậy', 'sau', 'rất',
            'mình', 'chỉ', 'thế', 'tôi', 'anh', 'chị', 'bạn', 'họ', 'nhiều', 'đâu', 'thêm', 'à', 'vâng'
        }
    
    # Loại bỏ dấu câu và chuyển thành chữ thường
    text = re.sub(r'[^\w\sÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ]', ' ', text.lower())
    
    # Tách thành từng từ
    words = text.split()
    
    # Loại bỏ stopwords và từ ngắn
    filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
    
    # Đếm tần suất
    word_freq = Counter(filtered_words)
    
    # Lấy top N từ khóa
    keywords = [word for word, _ in word_freq.most_common(top_n)]
    
    return keywords

def detect_offensive_words(text: str) -> Tuple[bool, List[str]]:
    """
    Phát hiện từ ngữ xúc phạm trong văn bản
    
    Args:
        text: Văn bản cần kiểm tra
        
    Returns:
        Tuple[bool, List[str]]: (Có từ xúc phạm hay không, danh sách từ xúc phạm)
    """
    # Tải danh sách từ ngữ xúc phạm tiếng Việt từ file nếu có
    try:
        with open('data/vietnamese_offensive_words.txt', 'r', encoding='utf-8') as f:
            offensive_words = set(line.strip() for line in f)
    except:
        # Danh sách từ ngữ xúc phạm mặc định nếu file không tồn tại
        # Chú ý: Chỉ dùng một số từ làm ví dụ, không liệt kê đầy đủ
        offensive_words = {
            'đồ', 'thằng', 'con', 'đm', 'vl', 'cmm', 'đcm', 'đéo', 'lồn', 'cặc', 'buồi',
            'ngu', 'dốt', 'khốn', 'chết', 'tiên sư', 'tổ sư', 'mẹ', 'má', 'cave', 'điếm'
        }
    
    # Chuẩn hóa văn bản
    normalized_text = text.lower()
    # Loại bỏ dấu câu và ký tự đặc biệt
    normalized_text = re.sub(r'[^\w\sÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ]', ' ', normalized_text)
    # Chuẩn hóa dấu cách
    normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
    
    # Tách thành từng từ
    words = normalized_text.split()
    
    # Tìm các từ xúc phạm
    found_offensive_words = [word for word in words if word in offensive_words]
    
    # Tìm các cụm từ xúc phạm
    for phrase in offensive_words:
        if ' ' in phrase and phrase in normalized_text:
            found_offensive_words.append(phrase)
    
    return len(found_offensive_words) > 0, found_offensive_words

def detect_hate_speech(text: str) -> Tuple[bool, List[str]]:
    """
    Phát hiện phát ngôn thù ghét trong văn bản
    
    Args:
        text: Văn bản cần kiểm tra
        
    Returns:
        Tuple[bool, List[str]]: (Có phát ngôn thù ghét hay không, danh sách cụm từ thù ghét)
    """
    # Tải danh sách từ ngữ thù ghét tiếng Việt từ file nếu có
    try:
        with open('data/vietnamese_hate_speech.txt', 'r', encoding='utf-8') as f:
            hate_phrases = set(line.strip() for line in f)
    except:
        # Danh sách từ ngữ thù ghét mặc định nếu file không tồn tại
        # Chú ý: Chỉ dùng một số từ làm ví dụ, không liệt kê đầy đủ
        hate_phrases = {
            'bọn', 'lũ', 'phường', 'đồ', 'quân', 'giết', 'tiêu diệt', 'xóa sổ', 'tàn sát',
            'diệt chủng', 'đánh đập', 'chém giết', 'loại trừ', 'trục xuất', 'cút về', 'cướp'
        }
    
    # Chuẩn hóa văn bản
    normalized_text = text.lower()
    
    # Tìm các từ/cụm từ thù ghét
    found_hate_phrases = []
    for phrase in hate_phrases:
        if phrase in normalized_text:
            found_hate_phrases.append(phrase)
    
    return len(found_hate_phrases) > 0, found_hate_phrases

def compute_text_statistics(text: str) -> Dict[str, Any]:
    """
    Tính toán các thống kê về văn bản
    
    Args:
        text: Văn bản cần phân tích
        
    Returns:
        Dict[str, Any]: Các thống kê về văn bản
    """
    if not text:
        return {
            "char_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "avg_word_length": 0,
            "avg_sentence_length": 0,
            "punctuation_count": 0,
            "uppercase_count": 0,
            "uppercase_ratio": 0,
            "digit_count": 0,
            "special_char_count": 0
        }
    
    # Đếm số ký tự
    char_count = len(text)
    
    # Đếm số từ
    words = re.findall(r'\b\w+\b', text.lower())
    word_count = len(words)
    
    # Đếm số câu
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]
    sentence_count = len(sentences)
    
    # Tính độ dài trung bình của từ
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
    
    # Tính độ dài trung bình của câu (số từ)
    if sentence_count > 0:
        sentence_words = [len(re.findall(r'\b\w+\b', s.lower())) for s in sentences]
        avg_sentence_length = sum(sentence_words) / sentence_count
    else:
        avg_sentence_length = 0
    
    # Đếm dấu câu
    punctuation_count = sum(1 for char in text if char in string.punctuation)
    
    # Đếm chữ hoa
    uppercase_count = sum(1 for char in text if char.isupper())
    uppercase_ratio = uppercase_count / char_count if char_count > 0 else 0
    
    # Đếm chữ số
    digit_count = sum(1 for char in text if char.isdigit())
    
    # Đếm ký tự đặc biệt
    special_char_count = sum(1 for char in text if not char.isalnum() and not char.isspace() and char not in string.punctuation)
    
    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_word_length": avg_word_length,
        "avg_sentence_length": avg_sentence_length,
        "punctuation_count": punctuation_count,
        "uppercase_count": uppercase_count,
        "uppercase_ratio": uppercase_ratio,
        "digit_count": digit_count,
        "special_char_count": special_char_count
    }