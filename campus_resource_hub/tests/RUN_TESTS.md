# How to Run Tests

## Prerequisites

Make sure you're in the `campus_resource_hub` directory:

```powershell
# If you're in the project root (AiDD_Final_Project)
cd campus_resource_hub

# Verify you're in the right place
dir tests
```

## Running Tests

### Run All Tests (excluding ai_eval)
```powershell
python -m pytest tests/ -v --ignore=tests/ai_eval
```

### Run Specific Test Files

**Security tests:**
```powershell
python -m pytest tests/test_security.py -v
```

**Booking logic tests:**
```powershell
python -m pytest tests/test_booking_logic.py -v
```

**Data access layer tests:**
```powershell
python -m pytest tests/test_data_access.py -v
```

**Integration tests:**
```powershell
python -m pytest tests/test_integration.py -v
```

### Run All Tests with Coverage
```powershell
# First install pytest-cov if not already installed
pip install pytest-cov

# Then run with coverage
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term --ignore=tests/ai_eval
```

## Common Issues

### "File or directory not found"
- **Solution:** Make sure you're in the `campus_resource_hub` directory
- Check with: `pwd` (Linux/Mac) or `Get-Location` (PowerShell)

### Import Errors
- **Solution:** Make sure you're running from `campus_resource_hub` directory
- The tests import from `src.*` which expects to be run from `campus_resource_hub`

### ai_eval Test Errors
- The `tests/ai_eval` directory has import issues
- **Solution:** Use `--ignore=tests/ai_eval` flag to skip those tests

## Test Results

Test results are saved to:
- `tests/test_results.txt` - Detailed pytest output
- `TEST_RESULTS.md` - Summary document

To regenerate test documentation:
```powershell
python generate_test_docs.py
```

