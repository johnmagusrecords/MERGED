import nltk
import spacy

# Download necessary NLTK resources
nltk.download('punkt')

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

def process_input(user_input):
    """
    Process user input and return the parsed result.
    """
    # Tokenize input using NLTK
    tokens = nltk.word_tokenize(user_input)
    
    # Process input with SpaCy
    doc = nlp(user_input)
    
    return tokens, doc
