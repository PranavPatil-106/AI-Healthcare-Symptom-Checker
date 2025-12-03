# Makefile for Healthcare Symptom Checker

# Variables
PYTHON := python3
PIP := pip
TEST_DIR := tests

# Default target
.PHONY: help
help:
	@echo "Healthcare Symptom Checker - Makefile Commands"
	@echo "=============================================="
	@echo "install          - Install dependencies"
	@echo "install-test     - Install test dependencies"
	@echo "run              - Run both backend and frontend"
	@echo "backend          - Run backend API server"
	@echo "frontend         - Run frontend Streamlit app"
	@echo "test             - Run tests"
	@echo "clean            - Clean Python cache files"

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Install test dependencies
.PHONY: install-test
install-test:
	$(PIP) install -r $(TEST_DIR)/requirements-test.txt

# Run both backend and frontend
.PHONY: run
run:
	$(PYTHON) run_app.py

# Run backend only
.PHONY: backend
backend:
	cd backend && $(PYTHON) main.py

# Run frontend only
.PHONY: frontend
frontend:
	cd frontend && streamlit run app.py

# Run tests
.PHONY: test
test:
	$(PYTHON) -m pytest $(TEST_DIR)/

# Clean Python cache files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/