from anthropic import Anthropic
import os
import base64
from typing import Dict, Any, Optional
import logfire
from functools import lru_cache
import hashlib

class AnthropicService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        logfire.instrument_anthropic(self.client)
        self.model = "claude-3-5-sonnet-latest"

    def _hash_pdf_content(self, pdf_content: Optional[bytes]) -> Optional[str]:
        """Hash PDF content to make it hashable for caching."""
        if pdf_content is None:
            return None
        return hashlib.sha256(pdf_content).hexdigest()

    @lru_cache(maxsize=100)
    def _cached_analyze(self, text: str, pdf_hash: Optional[str]) -> Dict[str, Any]:
        """Cached version of the analysis logic."""
        logfire.debug("Cache miss", text=text[:100])
        message_content = []
        
        # If we have document content (PDF or text), add it first
        if pdf_hash:
            logfire.debug("Adding PDF content to message")
            message_content.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": self._pdf_content_store.get(pdf_hash)
                },
                "cache_control": {"type": "ephemeral"},
                "citations": {"enabled": True}
            })
        
        # Add the text prompt
        message_content.append({
            "type": "text",
            "text": f"Please explain this text in simple terms: {text}"
        })
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0,
            system="You are a helpful assistant that explains complex documents in simple terms. Always cite your sources.",
            messages=[{
                "role": "user",
                "content": message_content
            }]
        )

        # Claude-3 returns content as a list of message parts
        content_text = ""
        for part in message.content:
            content_text += part.text
        
        logfire.info("Successfully analyzed text", content_length=len(content_text))
        
        return {
            "content": content_text,
            "citations": message.citations if hasattr(message, 'citations') else []
        }

    async def analyze_text(self, text: str, pdf_content: bytes = None) -> Dict[str, Any]:
        """
        Analyze text using Claude and return explanation with citations.
        If pdf_content is provided, it will be included in the message for context.
        """
        with logfire.span("analyze_text", text=text[:100] + "..." if len(text) > 100 else text):
            try:
                pdf_hash = self._hash_pdf_content(pdf_content)
                if pdf_hash:
                    # Store PDF content temporarily
                    if not hasattr(self, '_pdf_content_store'):
                        self._pdf_content_store = {}
                    self._pdf_content_store[pdf_hash] = base64.b64encode(pdf_content).decode()
                
                result = self._cached_analyze(text, pdf_hash)
                
                # Clean up stored PDF content
                if pdf_hash and hasattr(self, '_pdf_content_store'):
                    self._pdf_content_store.pop(pdf_hash, None)
                
                return result
            except Exception as e:
                logfire.error("Error analyzing text", error=str(e), exc_info=True)
                raise Exception(f"Error analyzing text: {str(e)}")

# Global instance
anthropic_service = AnthropicService()
