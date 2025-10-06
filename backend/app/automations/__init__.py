"""
Automations Package for NEW MCP Server
=====================================

This package contains all automation modules organized by functionality:

- meta_minds/          - AI-powered data analytics
- document_processing/ - PDF, Word, OCR processing
- workflow_builder/    - Visual workflow automation
- data_integration/    - API and database connections
- report_generator/    - Automated report creation
- ai_assistant/        - Natural language automation

Each automation is self-contained with its own:
- Core engine
- Workflows
- API routes
- Configuration
- Documentation
"""

from .meta_minds import *
from .document_processing import *
from .workflow_builder import *
from .data_integration import *
from .report_generator import *
from .ai_assistant import *
