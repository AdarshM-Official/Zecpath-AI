import spacy, sys
try:
    nlp = spacy.load('en_core_web_sm')
    print('Model loaded successfully')
except Exception as e:
    print('Failed to load model:', e)
