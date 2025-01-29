from typing import List, Optional
import base64
from pydantic import BaseModel
import re
import logfire

class Segment(BaseModel):
    text: str
    start_index: int
    end_index: int

class DocumentProcessor:
    def __init__(self):
        self.documents = {}  # In-memory storage for now

    def process_document(self, content: bytes, filename: str) -> str:
        """Process uploaded document and return document ID"""
        with logfire.span("process_document", filename=filename):
            try:
                doc_id = f"doc_{len(self.documents) + 1}"
                
                # Convert content based on file type
                if filename.lower().endswith('.pdf'):
                    logfire.debug("Processing PDF document", filename=filename)
                    processed_content = base64.b64encode(content).decode()
                    media_type = "application/pdf"
                    raw_content = content
                else:
                    logfire.debug("Processing text document", filename=filename)
                    processed_content = content.decode()
                    media_type = "text/plain"
                    raw_content = None
                
                # Create initial segments for text files
                segments = []
                if media_type == "text/plain":
                    segments = self._segment_text(processed_content)
                    logfire.info("Created text segments", count=len(segments))
                
                # Store document
                self.documents[doc_id] = {
                    "content": processed_content,
                    "raw_content": raw_content,
                    "media_type": media_type,
                    "filename": filename,
                    "segments": segments
                }
                
                logfire.info("Document processed successfully", doc_id=doc_id, media_type=media_type)
                return doc_id
            except Exception as e:
                logfire.error("Error processing document", 
                            filename=filename, 
                            error=str(e),
                            exc_info=True)
                raise

    def get_document(self, doc_id: str) -> Optional[dict]:
        """Retrieve document by ID"""
        with logfire.span("get_document", doc_id=doc_id):
            doc = self.documents.get(doc_id)
            if doc:
                logfire.debug("Document retrieved", doc_id=doc_id)
            else:
                logfire.warning("Document not found", doc_id=doc_id)
            return doc

    def _segment_text(self, text: str) -> List[Segment]:
        """Split text into logical segments"""
        with logfire.span("segment_text", text_length=len(text)):
            try:
                # Split by paragraphs and sentences
                segments = []
                current_index = 0
                
                # First split by double newlines (paragraphs)
                paragraphs = text.split('\n\n')
                
                for para in paragraphs:
                    if not para.strip():
                        continue
                        
                    # Split long paragraphs into sentences
                    if len(para) > 500:
                        sentences = re.split(r'(?<=[.!?])\s+', para)
                        for sent in sentences:
                            if not sent.strip():
                                continue
                            end_index = current_index + len(sent)
                            segments.append(Segment(
                                text=sent.strip(),
                                start_index=current_index,
                                end_index=end_index
                            ))
                            current_index = end_index + 1
                    else:
                        end_index = current_index + len(para)
                        segments.append(Segment(
                            text=para.strip(),
                            start_index=current_index,
                            end_index=end_index
                        ))
                        current_index = end_index + 2  # +2 for the newlines
                
                logfire.info("Text segmentation complete", 
                            segment_count=len(segments),
                            avg_segment_length=sum(len(s.text) for s in segments)/len(segments) if segments else 0)
                return segments
            except Exception as e:
                logfire.error("Error segmenting text", 
                            error=str(e),
                            text_length=len(text),
                            exc_info=True)
                raise

# Global instance
document_processor = DocumentProcessor()
