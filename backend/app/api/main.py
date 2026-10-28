from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

# Absolute imports to prevent ModuleNotFoundError
from backend.app.models.schemas import ScanRequest, ScanResponse, PIIFinding
from backend.app.core.engine import HybridPIIEngine
from backend.app.services.connector import DataConnector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("privexis-api")

app = FastAPI(title="Privexis Elite API", version="2.0.0")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
engine = HybridPIIEngine()
connector = DataConnector(base_path="data")

@app.get("/")
async def root():
    return {"status": "online", "message": "Privexis Elite Backend is running"}

@app.post("/scan", response_model=ScanResponse)
async def scan_file(request: ScanRequest):
    start_time = time.time()
    logger.info(f"Starting scan for file: {request.file_path}")

    try:
        findings = []
        total_cols = 0

        # Get all tables in the file
        tables = list(connector.get_tables(request.file_path))

        for table in tables:
            # Scan each column in the table
            for i, col_name in enumerate(table.columns):
                total_cols += 1
                # Extract samples for analysis
                samples = connector.sample_column(table, i, sample_size=request.sample_size)

                # Analyze column using the Hybrid Engine
                finding = engine.analyze_column(
                    source=table.source,
                    table=table.name,
                    column=col_name,
                    values=samples
                )
                findings.append(finding)

        # Filter only those where PII was detected
        pii_detected = [f for f in findings if f.pii_class != "NONE"]

        execution_time = time.time() - start_time

        return ScanResponse(
            total_columns_scanned=total_cols,
            pii_detected_count=len(pii_detected),
            findings=pii_detected,
            execution_time=round(execution_time, 3)
        )

    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
