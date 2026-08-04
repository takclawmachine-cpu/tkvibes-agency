"""
TKVibes — Lead Engine Test Suite
Conftest: makes src package importable via sys.path manipulation.
"""
import sys
import os
import logging

logging.disable(logging.CRITICAL)

# Add project root so 'src' package is findable
PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJ_ROOT not in sys.path:
    sys.path.insert(0, PROJ_ROOT)

# Now import via src package path
from src.models import Lead, SCHEMA
from src.score import score_lead
from src.config import load_config