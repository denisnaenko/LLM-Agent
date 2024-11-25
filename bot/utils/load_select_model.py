from sentence_transformers import SentenceTransformer

def load_select_model(model_name="cointegrated/rubert-tiny2"):
    """Загружает указанную модель SentenceTransformer."""
    return SentenceTransformer(model_name)