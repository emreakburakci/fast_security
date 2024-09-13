import fitz  # PyMuPDF
import docx
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

def initialize_nltk():
    # Download necessary NLTK data

    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('averaged_perceptron_tagger_eng')
    nltk.download('maxent_ne_chunker')
    nltk.download('maxent_ne_chunker_tab')
    nltk.download('words')
    nltk.download('vader_lexicon')


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def tokenize_text(text):
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    return words, sentences

def word_frequency(text):
    words, _ = tokenize_text(text)
    return FreqDist(words)

def pos_tags(text):
    words, _ = tokenize_text(text)
    return pos_tag(words)

def named_entities(text):
    pos_tags_list = pos_tags(text)
    return ne_chunk(pos_tags_list)

def sentiment_analysis(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)

def ngrams(text, n=2):
    words, _ = tokenize_text(text)
    return list(nltk.ngrams(words, n))

def concordance(text, word):
    words, _ = tokenize_text(text)
    text_obj = nltk.Text(words)
    return text_obj.concordance_list(word, lines=5)

def extract_text_from_file(file_path, file_type):
    if file_type == "pdf":
        text = extract_text_from_pdf(file_path)
    elif file_type == "docx":
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type")
    
    return text

# Example usage
if __name__ == "__main__":
    file_path = "example.pdf"  # Change to your file path
    file_type = "pdf"  # Change to "docx" if analyzing a DOCX file
    text = extract_text_from_file(file_path, file_type)
    
    # Print results
    print("Word Frequency:", word_frequency(text))
    print("POS Tags:", pos_tags(text))
    print("Named Entities:", named_entities(text))
    print("Sentiment:", sentiment_analysis(text))
    print("Bigrams:", ngrams(text, 2))
    print("Trigrams:", ngrams(text, 3))
    print("Concordance:", concordance(text, "example"))