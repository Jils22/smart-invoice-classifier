import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def ensure_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except:
        nltk.download('stopwords')
    try:
        nltk.data.find('corpora/wordnet')
    except:
        nltk.download('wordnet')

ensure_nltk()

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\b(invoice id|invoice|account no:|account)\b', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)
