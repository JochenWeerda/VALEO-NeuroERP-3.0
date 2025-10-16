"""
OpenAI Service
Handles OpenAI API interactions for LLM functionality
"""

import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# Global OpenAI client
_openai_client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client instance"""
    global _openai_client
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


async def generate_completion(
    prompt: str,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    system_message: str = None
) -> str:
    """
    Generate text completion using OpenAI

    Args:
        prompt: User prompt
        model: Model to use (defaults to settings.OPENAI_MODEL)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        system_message: Optional system message

    Returns:
        Generated text
    """
    client = get_openai_client()
    model = model or settings.OPENAI_MODEL

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI completion failed: {e}")
        raise


async def analyze_text(
    text: str,
    task: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze text using OpenAI for specific tasks

    Args:
        text: Text to analyze
        task: Analysis task description
        context: Additional context

    Returns:
        Analysis results
    """
    context_str = ""
    if context:
        context_str = f"\nContext: {context}"

    prompt = f"""
Task: {task}

Text to analyze:
{text}{context_str}

Please provide a structured analysis with key insights and recommendations.
Format your response as JSON with the following structure:
{{
    "insights": ["key insight 1", "key insight 2"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "confidence": 0.0-1.0,
    "metadata": {{}}
}}
"""

    system_message = "You are an expert agricultural ERP analyst. Provide accurate, actionable insights based on the provided data."

    try:
        response = await generate_completion(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3
        )

        # Try to parse JSON response
        import json
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "insights": [response],
            "recommendations": [],
            "confidence": 0.5,
            "metadata": {"raw_response": response}
        }
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        raise


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for texts using OpenAI

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    client = get_openai_client()

    try:
        response = await client.embeddings.create(
            input=texts,
            model=settings.OPENAI_EMBEDDING_MODEL
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise


async def suggest_autocomplete(
    query: str,
    context: str,
    domain: str = "general",
    max_suggestions: int = 5
) -> List[str]:
    """
    Generate autocomplete suggestions using OpenAI

    Args:
        query: Current query text
        context: Context information
        domain: Domain context (e.g., "procurement", "inventory")
        max_suggestions: Maximum number of suggestions

    Returns:
        List of autocomplete suggestions
    """
    prompt = f"""
Based on the current query and context, suggest {max_suggestions} relevant completions.

Domain: {domain}
Current Query: "{query}"
Context: {context}

Provide suggestions that would naturally complete or extend the query.
Focus on practical, commonly used terms in agricultural ERP systems.
Return only the suggestions as a JSON array of strings.
"""

    system_message = "You are an autocomplete assistant for an agricultural ERP system. Provide relevant, practical suggestions."

    try:
        response = await generate_completion(
            prompt=prompt,
            system_message=system_message,
            temperature=0.5,
            max_tokens=200
        )

        import json
        suggestions = json.loads(response)
        return suggestions[:max_suggestions] if isinstance(suggestions, list) else []
    except Exception as e:
        logger.error(f"Autocomplete suggestion failed: {e}")
        return []