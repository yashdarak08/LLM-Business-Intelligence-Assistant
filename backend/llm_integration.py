# backend/llm_integration.py

import logging
import time
import json
from transformers import pipeline, set_seed, AutoTokenizer, AutoModelForCausalLM
from backend.config import LLM_MODEL_NAME, LLM_MAX_LENGTH
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Initialize the text generation pipeline with a set seed for reproducibility
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def initialize_generator():
    """Initialize the text generation pipeline with retry logic."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(LLM_MODEL_NAME)
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
        set_seed(42)
        return generator
    except Exception as e:
        logger.error(f"Error initializing LLM generator: {e}")
        raise

# Initialize generator on module import
try:
    generator = initialize_generator()
except Exception as e:
    logger.error(f"Failed to initialize LLM generator: {e}")
    # Provide a fallback function that will attempt to initialize on demand
    def get_generator():
        global generator
        if generator is None:
            generator = initialize_generator()
        return generator
else:
    # If initialization succeeded, simple pass-through function
    def get_generator():
        return generator

def extract_response(generated_text, prompt):
    """
    Extracts the model's response from the generated text by removing the prompt.
    """
    if generated_text.startswith(prompt):
        return generated_text[len(prompt):].strip()
    return generated_text.strip()

def clean_response(response):
    """
    Cleans up the response by removing incomplete sentences at the end.
    """
    # Find the last complete sentence
    end_markers = ['.', '!', '?']
    last_marker = max(response.rfind(marker) for marker in end_markers)
    
    if last_marker > 0:
        return response[:last_marker + 1].strip()
    return response.strip()

def generate_response(query: str, retrieved_chunks: list):
    """
    Generates a business insight response by combining the query with retrieved context.
    """
    start_time = time.time()
    
    try:
        # Get the active generator
        active_generator = get_generator()
        
        # Extract text from retrieved chunks and format context
        context = "\n\n".join([f"Document: {chunk.get('file_path', 'Unknown')}\n{chunk.get('text', '')}" 
                             for chunk in retrieved_chunks])
        
        # Create prompt with instructions for structured output
        prompt = f"""You are a business intelligence assistant.

Given the following context extracted from business documents:
{context}

Answer the following query with actionable insights:
{query}

Provide your response in the following format:
SUMMARY: A brief summary of your findings
KEY INSIGHTS:
- First key insight
- Second key insight
- Additional insights as needed
RECOMMENDATIONS:
- First recommendation
- Second recommendation
- Additional recommendations as needed

Answer:"""

        logger.info("Generating response for query: %s", query)
        
        # Generate response with the model
        response = active_generator(
            prompt, 
            max_length=len(prompt.split()) + LLM_MAX_LENGTH,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        # Extract and clean the generated text
        generated_text = response[0]["generated_text"]
        extracted_response = extract_response(generated_text, prompt)
        clean_result = clean_response(extracted_response)
        
        # Measure generation time
        end_time = time.time()
        generation_time = end_time - start_time
        logger.debug(f"LLM response generated in {generation_time:.2f} seconds")
        
        return clean_result
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return f"I apologize, but I encountered an error while generating insights. Error: {str(e)}"

def generate_structured_response(query: str, retrieved_chunks: list):
    """
    Generates a business insight response with a structured JSON output.
    """
    try:
        # Get the active generator
        active_generator = get_generator()
        
        # Extract text from retrieved chunks and format context
        context = "\n\n".join([f"Document: {chunk.get('file_path', 'Unknown')}\n{chunk.get('text', '')}" 
                             for chunk in retrieved_chunks])
        
        # Create prompt with instructions for structured JSON output
        prompt = f"""You are a business intelligence assistant.

Given the following context extracted from business documents:
{context}

Answer the following query with actionable insights:
{query}

Provide your response in valid JSON format with the following structure:
{{
  "summary": "A brief summary of your findings",
  "key_insights": [
    "First key insight",
    "Second key insight",
    "Additional insights as needed"
  ],
  "recommendations": [
    "First recommendation",
    "Second recommendation",
    "Additional recommendations as needed"
  ],
  "sources": [
    "Source 1",
    "Source 2"
  ]
}}

JSON Response:"""

        logger.info("Generating structured response for query: %s", query)
        
        # Generate response with the model
        response = active_generator(
            prompt, 
            max_length=len(prompt.split()) + LLM_MAX_LENGTH,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        # Extract and parse the generated JSON
        generated_text = response[0]["generated_text"]
        extracted_response = extract_response(generated_text, prompt)
        
        # Try to parse as JSON, fall back to regular text if it fails
        try:
            # Find the first { and last } to extract the JSON part
            start_idx = extracted_response.find('{')
            end_idx = extracted_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = extracted_response[start_idx:end_idx]
                structured_response = json.loads(json_str)
                return structured_response
            else:
                logger.warning("Could not find valid JSON in the response")
                return {"error": "Invalid JSON format", "raw_response": generate_response(query, retrieved_chunks)}
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {"error": "JSON parsing error", "raw_response": generate_response(query, retrieved_chunks)}
            
    except Exception as e:
        logger.error(f"Error generating structured response: {e}")
        return {"error": str(e), "raw_response": "Error generating response"}