# backend/llm_integration.py

import logging
from transformers import pipeline, set_seed
from backend.config import LLM_MODEL_NAME

logger = logging.getLogger(__name__)

# Initialize the text generation pipeline with a set seed for reproducibility
generator = pipeline("text-generation", model=LLM_MODEL_NAME)
set_seed(42)

def generate_response(query: str, retrieved_chunks: list):
    """
    Generates a business insight response by combining the query with retrieved context.
    """
    context = "\n".join([chunk["text"] for chunk in retrieved_chunks])
    prompt = f"""You are a business intelligence assistant.
Given the following context extracted from business documents:
{context}

Answer the following query with actionable insights:
{query}

Answer:"""
    logger.info("Generating response for query: %s", query)
    response = generator(prompt, max_length=250, num_return_sequences=1)
    generated_text = response[0]["generated_text"]
    logger.debug("Generated response: %s", generated_text)
    return generated_text
