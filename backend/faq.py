import numpy as np

from nltk import WordPunctTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def tokenize(text):
    tokenizer = WordPunctTokenizer()
    return list(map(str.lower, tokenizer.tokenize(text)))


def preprocess(text):
    return ' '.join(tokenize(text))


def make_vectorizer(questions):
    texts = [item
             for question in questions
             for item in (question['question'], *question['paraphrases'])]
    vectorizer = TfidfVectorizer(stop_words='english', tokenizer=tokenize).fit(texts)
    return vectorizer


def transform(vectorizer, text):
    text = preprocess(text)
    return np.array(vectorizer.transform([text]).todense())


def get_word_weights(vectorizer, text):
    norm = transform(vectorizer, text)
    word2weight = {word: weight for word, weight in zip(vectorizer.get_feature_names(), norm.ravel())}
    return np.array([1 / len(text.split())] * len(text.split()))


def get_embedding(vectorizer, model, text):
    text = preprocess(text)
    weights = get_word_weights(vectorizer, text)
    embeddings = np.array([model.get_vector(word) for word in text.split()])
    return np.matmul(embeddings.T, weights).reshape(1, -1)


def get_top_answer(vectorizer, model, questions, input_question):
    scores = []
    emb = get_embedding(vectorizer, model, input_question)
    for question in questions:
        score = cosine_similarity(emb, get_embedding(vectorizer, model, question['question']))
        score = max(score, *[cosine_similarity(emb, get_embedding(vectorizer, model, paraphrase))
                             for paraphrase in question['paraphrases']])
        scores.append(score)
    return questions[np.argmax(scores)]['action']
