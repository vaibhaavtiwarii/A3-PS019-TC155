from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class PIIFinding(BaseModel):
    source: str
    table: str
    column: str
    pii_class: str
    confidence: float
    confidence_level: ConfidenceLevel
    evidence: str
    name_score: float
    value_score: float
    matched_value_sample: Optional[str] = None

class ScanRequest(BaseModel):
    file_path: str
    sample_size: int = 50
    rules_config_path: Optional[str] = "config/rules.yaml"

class ScanResponse(BaseModel):
    total_columns_scanned: int
    pii_detected_count: int
    findings: List[PIIFinding]
    execution_time: float
