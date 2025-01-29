from fastapi import FastAPI, UploadFile, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import logfire
import json

# Load environment variables from .env file
load_dotenv()

from .services.document import document_processor
from .services.anthropic import anthropic_service
from .models.document import DocumentSegment, DocumentResponse, DocumentMetadata, AnalysisRequest, AnalysisResponse

logfire.configure()
logfire.instrument_pydantic()
app = FastAPI()
logfire.instrument_fastapi(app)
templates = Jinja2Templates(directory="src/templates")

# Serve static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile):
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    try:
        content = await file.read()
        doc_id = document_processor.process_document(content, file.filename)
        doc = document_processor.get_document(doc_id)
        
        # For PDFs, we need to get an initial analysis from Claude
        if doc["media_type"] == "application/pdf":
            with logfire.span("extract_pdf_text"):
                # First, get the text content from the PDF
                result = await anthropic_service.analyze_text(
                    "Please extract all the text content from this PDF, preserving the original formatting and structure. Break it into logical segments separated by two newlines. Do not explain or modify the text, just extract it exactly as it appears.",
                    doc["raw_content"]
                )
                
                # Create segments from the extracted text
                text_segments = [
                    DocumentSegment(
                        text=segment.strip(),
                        start_index=idx * 1000,
                        end_index=(idx + 1) * 1000 - 1
                    )
                    for idx, segment in enumerate(result["content"].split("\n\n"))
                    if segment.strip()
                ]
                
                # Store the original text segments
                document_processor.documents[doc_id]["segments"] = text_segments
                
                # Analyze which segments need explanation
                with logfire.span("analyze_segment_complexity"):
                    complexity_analysis = await anthropic_service.analyze_text(
                        """For each of the following text segments, determine if it needs explanation by checking if:
                        1. It contains technical terms or jargon
                        2. It has complex sentence structure
                        3. It describes non-trivial concepts
                        4. It's not already a simple explanation
                        
                        Return a JSON array where each item has:
                        - "needs_explanation": boolean
                        - "reason": brief explanation of why or why not
                        
                        Here are the segments to analyze:
                        """ + "\n---\n".join(f"Segment {i+1}:\n{s.text}" for i, s in enumerate(text_segments)),
                        doc["raw_content"]
                    )
                    
                    try:
                        # Extract the JSON array from Claude's response
                        analysis_start = complexity_analysis["content"].find("[")
                        analysis_end = complexity_analysis["content"].rfind("]") + 1
                        complexity_results = json.loads(complexity_analysis["content"][analysis_start:analysis_end])
                        logfire.info("Complexity analysis complete", 
                                   total_segments=len(text_segments),
                                   segments_needing_explanation=sum(1 for r in complexity_results if r["needs_explanation"]))
                    except Exception as e:
                        logfire.error("Error parsing complexity analysis", error=str(e))
                        complexity_results = [{"needs_explanation": True, "reason": "Error analyzing complexity"}] * len(text_segments)
                
                # Now get explanations only for segments that need them
                with logfire.span("generate_explanations"):
                    explanations = []
                    for i, (segment, analysis) in enumerate(zip(text_segments, complexity_results)):
                        if analysis["needs_explanation"]:
                            logfire.debug("Generating explanation for segment", 
                                        segment_index=i,
                                        reason=analysis["reason"])
                            explanation = await anthropic_service.analyze_text(
                                f"Please explain this text segment in simple terms: {segment.text}",
                                doc["raw_content"]  # Pass full PDF for context
                            )
                            explanations.append(DocumentSegment(
                                text=explanation["content"],
                                start_index=segment.start_index,
                                end_index=segment.end_index
                            ))
                        else:
                            logfire.debug("Skipping explanation for simple segment", 
                                        segment_index=i,
                                        reason=analysis["reason"])
                            # For segments that don't need explanation, just echo the original text
                            explanations.append(DocumentSegment(
                                text=segment.text,
                                start_index=segment.start_index,
                                end_index=segment.end_index
                            ))
                    
                    # Store the explanations
                    document_processor.documents[doc_id]["explanations"] = explanations
                    document_processor.documents[doc_id]["complexity_analysis"] = complexity_results
                    logfire.info("Generated explanations", 
                               total_segments=len(explanations),
                               segments_explained=sum(1 for r in complexity_results if r["needs_explanation"]))
        
        return DocumentResponse(
            metadata=DocumentMetadata(
                id=doc_id,
                filename=file.filename,
                media_type=doc["media_type"]
            ),
            segments=doc["segments"],
            explanations=doc.get("explanations", [])
        )
    except Exception as e:
        logfire.error("Error processing upload", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    doc = document_processor.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        metadata=DocumentMetadata(
            id=doc_id,
            filename=doc["filename"],
            media_type=doc["media_type"]
        ),
        segments=doc["segments"],
        explanations=doc.get("explanations", [])
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_segment(request: AnalysisRequest):
    try:
        doc = document_processor.get_document(request.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get analysis from Claude, passing PDF content if it's a PDF
        result = await anthropic_service.analyze_text(
            request.text,
            pdf_content=doc.get("raw_content") if doc["media_type"] == "application/pdf" else None
        )
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))