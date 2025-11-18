"""FastAPI Main Application"""

import warnings
# Suppress Pydantic deprecation warnings from third-party libraries
warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional, AsyncGenerator
from datetime import datetime
import sys
import os
import json
import asyncio
import tempfile
from dotenv import load_dotenv

# Load environment variables from project root .env file
# Go up four levels from src/api/main.py to project root
project_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crew.crew import AdQualityRaterCrew
from utils.logger import logger

app = FastAPI(
    title="Ads Quality Rater API",
    version="1.0.0",
    description="KI-basierte Bewertung von Ad-LP-Kohärenz und Markenkonformität",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if Gemini API key is set
        gemini_key = os.getenv("GEMINI_API_KEY")
        gemini_status = "healthy" if gemini_key else "unhealthy"

        overall = "healthy" if gemini_status == "healthy" else "degraded"

        return {
            "status": overall,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "gemini": gemini_status,
            },
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {"status": "unhealthy", "error": str(e)}


@app.post("/api/v1/analyze/stream")
async def analyze_ad_stream(
    landing_page_url: str = Form(...),
    ad_file: UploadFile = File(...),
    brand_guidelines: Optional[str] = Form(None),
    target_audience: Optional[str] = Form(None),
    campaign_goal: Optional[str] = Form(None),
):
    """
    Streaming endpoint: Start Ad Quality Analysis with real-time logs

    Requires an uploaded ad image file (ad_file) and landing page URL
    Returns Server-Sent Events with logs and final result
    """
    # Validate ad_file is provided
    if not ad_file:
        raise HTTPException(status_code=400, detail="ad_file (uploaded image) is required")

    # Validate landing_page_url is accessible
    if not landing_page_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="landing_page_url must be a valid HTTP/HTTPS URL")

    # Parse brand guidelines if provided
    parsed_guidelines = None
    if brand_guidelines:
        try:
            parsed_guidelines = json.loads(brand_guidelines)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="brand_guidelines must be valid JSON")

    # Validate file size (max 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    content = await ad_file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is 10MB, got {len(content) / (1024*1024):.1f}MB")

    # Validate it's actually an image
    if not ad_file.content_type or not ad_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File must be an image, got {ad_file.content_type}")

    # Save to temporary file
    file_extension = os.path.splitext(ad_file.filename or "image.jpg")[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events with logs and result"""
        import threading
        import queue
        import sys
        import time

        log_queue = queue.Queue()
        result_holder = {"result": None, "error": None}
        crew_running = threading.Event()

        def run_crew():
            """Run crew in thread and capture ALL output"""
            old_stdout = sys.stdout
            old_stderr = sys.stderr

            try:
                # Log start BEFORE redirecting output so it definitely appears
                log_queue.put({"type": "log", "data": "🚀 Starting analysis..."})

                # Capture console output periodically
                from io import StringIO

                # Create string buffer for output
                output_buffer = StringIO()

                # Redirect stdout/stderr
                sys.stdout = output_buffer
                sys.stderr = output_buffer

                crew_running.set()

                log_queue.put({"type": "log", "data": f"📁 Ad file: {temp_file_path}"})
                log_queue.put({"type": "log", "data": f"🌐 Landing page: {landing_page_url}"})

                # Create crew and start analysis
                log_queue.put({"type": "log", "data": "🏗️ Creating crew..."})
                crew = AdQualityRaterCrew(
                    ad_url=temp_file_path,
                    landing_page_url=landing_page_url,
                    brand_guidelines=parsed_guidelines,
                    target_audience=target_audience,
                    campaign_goal=campaign_goal,
                )
                log_queue.put({"type": "log", "data": "✅ Crew created successfully"})

                # Start a thread to periodically flush output
                last_position = [0]  # Use list to make it mutable in closure
                stop_flushing = threading.Event()

                def flush_output():
                    while not stop_flushing.is_set():
                        try:
                            output_buffer.seek(last_position[0])
                            new_content = output_buffer.read()
                            if new_content:
                                # Split into lines and send each
                                for line in new_content.splitlines():
                                    if line.strip():
                                        log_queue.put({"type": "log", "data": line})
                                last_position[0] = output_buffer.tell()
                            time.sleep(0.1)  # Check every 100ms
                        except:
                            pass

                flush_thread = threading.Thread(target=flush_output, daemon=True)
                flush_thread.start()

                # Run the crew (this blocks) - now returns text
                log_queue.put({"type": "log", "data": "⚙️ Running crew analysis..."})
                result_text = crew.kickoff()

                # Debug logging
                print(f"[DEBUG] Crew returned result type: {type(result_text)}", file=old_stderr)
                print(f"[DEBUG] Result length: {len(str(result_text))} chars", file=old_stderr)
                print(f"[DEBUG] First 100 chars: {str(result_text)[:100]}", file=old_stderr)

                log_queue.put({"type": "log", "data": f"✅ Analysis complete! Result length: {len(str(result_text))} chars"})
                result_holder["result"] = str(result_text)

                # Stop flushing thread and get final output
                stop_flushing.set()
                flush_thread.join(timeout=1)

                # Get any remaining output
                output_buffer.seek(last_position[0])
                remaining = output_buffer.read()
                if remaining:
                    for line in remaining.splitlines():
                        if line.strip():
                            log_queue.put({"type": "log", "data": line})

                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr

            except Exception as e:
                import traceback
                error_msg = f"Crew execution error: {str(e)}"
                error_trace = traceback.format_exc()

                # Restore stdout/stderr first so we can log properly
                sys.stdout = old_stdout
                sys.stderr = old_stderr

                # Log the error with full traceback
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                print(f"[TRACEBACK] {error_trace}", file=sys.stderr)

                log_queue.put({"type": "log", "data": f"❌ {error_msg}"})
                log_queue.put({"type": "log", "data": f"Details: {error_trace[:500]}"})
                result_holder["error"] = error_msg
            finally:
                crew_running.clear()
                log_queue.put({"type": "log", "data": "🏁 Crew execution finished"})
                # Don't send "done" here - we'll send it after we've sent the result
                # log_queue.put({"type": "done"})

        # Start crew in background thread
        crew_thread = threading.Thread(target=run_crew, daemon=True)
        crew_thread.start()

        # Stream logs as they come
        while True:
            try:
                event = log_queue.get(timeout=0.1)

                # Send the event
                yield f"data: {json.dumps(event)}\n\n"

            except queue.Empty:
                # Check if crew is done
                if not crew_running.is_set() and not crew_thread.is_alive():
                    # Crew has finished, send final result
                    if result_holder["result"]:
                        result_text = result_holder["result"]
                        yield f"data: {json.dumps({'type': 'result', 'data': result_text})}\n\n"
                    elif result_holder["error"]:
                        yield f"data: {json.dumps({'type': 'error', 'data': result_holder['error']})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'data': 'No result received from crew'})}\n\n"
                    break

                # Send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                await asyncio.sleep(0.1)

        crew_thread.join(timeout=1)

        # Cleanup temp file after streaming is complete
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info("Cleaned up temp file", path=temp_file_path)
            except Exception as e:
                logger.warning("Failed to cleanup temp file", path=temp_file_path, error=str(e))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ads Quality Rater API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
