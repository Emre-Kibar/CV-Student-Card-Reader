from backend.database import SessionLocal
from backend.models import Scan, ScanField

db = SessionLocal()
scans = db.query(Scan).order_by(Scan.id.desc()).limit(5).all()

print(f"Found {len(scans)} recent scans:")
for scan in scans:
    print(f"Scan ID: {scan.id}, Status: {scan.status}, File: {scan.filename}")
    if scan.error_message:
        print(f"  ❌ Error: {scan.error_message}")
    
    fields = db.query(ScanField).filter(ScanField.scan_id == scan.id).all()
    print(f"  - Fields found in DB: {len(fields)}")
    for f in fields[:3]:
        print(f"    - Text: {f.text[:20]}..., Conf: {f.confidence}, Box: {f.x},{f.y} {f.width}x{f.height}")
