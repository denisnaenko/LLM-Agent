from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def load_promt_model(model_name="distilgpt2", max_length=512):
    """
    Загружает модель и настраивает pipeline для генерации текста.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    llm_pipeline = pipeline(
        "text-generation", model=model, tokenizer=tokenizer, max_length=max_length
    )
    return llm_pipeline
