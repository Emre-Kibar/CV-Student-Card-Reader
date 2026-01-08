import sys
import os
import shutil
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

# Append parent directory to path to import main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import models, schemas, database
from main import IDCardProcessor

# Constants
UPLOAD_DIR = "input_images"
OUTPUT_DIR = "output"

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Student Card Reader API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")
# We also might want to serve input images 
app.mount("/input", StaticFiles(directory=UPLOAD_DIR), name="input")


# Dependencies
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Progress tracking (simple in-memory for now)
# In a real app with multiple workers, this should be in Redis
class ProgressTracker:
    def __init__(self):
        self.progress = {}  # scan_id -> {status, percent}

    def update(self, scan_id, status, percent):
        self.progress[scan_id] = {"status": status, "percent": percent}

    def get(self, scan_id):
        return self.progress.get(scan_id, {"status": "unknown", "percent": 0})

tracker = ProgressTracker()

def process_scan_background(scan_id: int, file_path: str, db: Session):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        return

    def callback(status, percent):
        tracker.update(scan_id, status, percent)
        # Update DB status if significant change? 
        # For now just keep in memory for realtime, DB for final state.
    
    try:
        tracker.update(scan_id, "starting", 0)
        scan.status = "processing"
        db.commit()

        processor = IDCardProcessor(debug_mode=False)
        result = processor.process_image(file_path, OUTPUT_DIR, progress_callback=callback)

        if result:
            scan.status = "completed"
            
            # Save extracted fields to DB
            # We need to map `result` structure to our DB models.
            # result['extracted_texts'] is just a list of strings currently. 
            # Ideally main.py should return structured field data.
            # But based on main.py, `extracted_texts` comes from `text_extractor.extract_text`
            # which returns a list of strings.
            # `field_extractor.extract_fields` returns `field_info` (x, y, path).
            # `text_extractor.extract_text` takes `field_info` but returns only text list.
            # I should prefer modifying main.py to return combined info, but to minimize changes,
            # I will re-implement the combination here or check if I can easily tweak main.py's return.
            # main.py result: 
            # {
            #     'image_path': image_path,
            #     'base_name': base_name,
            #     'card_image': result['card_image'],
            #     'extracted_texts': extracted_texts
            # }
            # Wait, `extracted_texts` are just strings. 
            # If I want coordinates, I need to know which text belongs to which field.
            
            # CRITICAL: main.py implementation of `extract_text` returns a LIST of strings.
            # It loses the coordinate information.
            # I really should modify `TextExtractor.extract_text` to return a dictionary or objects with text AND coordinates.
            # But let's check `TextExtractor.extract_text`.
            # It calls `pytesseract` on each crop.
            
            # For now, I will assume the strings are in order and I can't easily get coords without refactoring.
            # Wait, `field_extractor` returns `field_info` which has coords.
            # `text_extractor` filters fields and sorts them.
            # I should modify `TextExtractor` to return the full object.
            
            # TEMPORARY: Just save the texts without specific coords for now, 
            # OR better, update main.py/text_extraction.py to return better data.
            # Given the requirement "Visualize individual detected field sections ... Display field coordinates",
            # I MUST refactor text_extraction.py to return structured data.
            
            # Let's assume for this step I will refactor text_extraction.py in the NEXT step.
            # I'll just save what I have.
            
            # Save combined info
            base_name = result['base_name']
            for i, field_data in enumerate(result['extracted_texts']):
                # Now we expect field_data to be a dict
                if isinstance(field_data, dict):
                    # We need to make the path relative to output/ or use the full web path
                    # field_data['path'] is absolute local path. 
                    # We want relative to where static files are served?
                    # or just the filename if it's in output/
                    field_filename = os.path.basename(field_data['path'])
                    # It is in output/{base_name}_fields/{filename}
                    # We need the relative path from project root or output dir.
                    # 'path' is e.g. /Users/.../output/basename_fields/x_y.jpg
                    
                    # Construct relative path for DB
                    relative_path = f"output/{base_name}_fields/{field_filename}"
                    
                    db_field = models.ScanField(
                        scan_id=scan.id,
                        text=field_data['text'],
                        x=field_data.get('x', 0),
                        y=field_data.get('y', 0),
                        width=field_data.get('width', 0),
                        height=field_data.get('height', 0),
                        image_path=relative_path,
                        confidence=0.9 # Mock confidence
                    )
                    db.add(db_field)
                else:
                    # Fallback for string
                   pass
            # Update scan paths
            # The processor saves `output/{base_name}_detected_card.jpg`
            base_name = result['base_name']
            scan.card_image_path = f"output/{base_name}_detected_card.jpg"
            
        else:
            scan.status = "failed"
            scan.error_message = "Card detection failed"
        
        db.commit()
    
    except Exception as e:
        scan.status = "failed"
        scan.error_message = str(e)
        db.commit()
        print(f"Error processing scan {scan_id}: {e}")

@app.post("/api/scan", response_model=schemas.Scan)
async def upload_scan(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create DB record
    db_scan = models.Scan(
        filename=file.filename,
        original_image_path=f"input/{file.filename}",
        status="pending"
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    # Trigger background processing
    background_tasks.add_task(process_scan_background, db_scan.id, file_path, db)
    
    return db_scan

@app.get("/api/scans", response_model=List[schemas.Scan])
def get_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scans = db.query(models.Scan).order_by(models.Scan.created_at.desc()).offset(skip).limit(limit).all()
    return scans

@app.get("/api/scans/{scan_id}", response_model=schemas.Scan)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@app.delete("/api/scans/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(models.Scan).filter(models.Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Delete files?
    # TODO: Implement file deletion cleanup
    
    db.delete(scan)
    db.commit()
    return {"ok": True}

@app.get("/api/scan/{scan_id}/progress")
def get_scan_progress(scan_id: int):
    return tracker.get(scan_id)
