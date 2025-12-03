# Healthcare Symptom Checker

A comprehensive healthcare symptom checking application built with FastAPI (backend) and Streamlit (frontend) that leverages LLM technology to provide educational information about possible medical conditions based on user-input symptoms.

## 🚨 Important Medical Disclaimer

**This tool provides educational information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for any medical concerns. This application does not provide medical diagnoses and should not be used to make decisions about your health.**

## Features

- 🔍 **Symptom Analysis**: Enter your symptoms and receive possible conditions with likelihood assessments
- 🤖 **AI-Powered Insights**: Uses advanced LLM technology (Google Gemini) for medical education
- 📚 **Educational Focus**: Provides information for learning purposes, not diagnosis
- 💾 **Query History**: Stores your previous symptom checks for reference
- 🛡️ **Safety First**: Comprehensive disclaimers and safety warnings throughout

## Technical Architecture

### Backend (FastAPI)
- RESTful API for symptom checking
- LLM integration (Google Gemini Pro)
- SQLite database for query history
- Comprehensive error handling and fallbacks

### Frontend (Streamlit)
- Responsive user interface
- Symptom input form
- Results display with expandable sections
- Query history viewer

## Prerequisites

- Python 3.8+
- Google Gemini API key (for LLM integration)
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd healthcare-symptom-checker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

1. Start the backend API:
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8080`

2. In a new terminal, start the frontend:
   ```bash
   cd frontend
   streamlit run app.py
   ```
   The frontend will open in your browser at `http://localhost:8501`

3. Describe your symptoms in the text area and click "Check Symptoms"

## API Endpoints

- `GET /` - Health check endpoint
- `POST /check_symptoms/` - Submit symptoms for analysis
- `GET /history/` - Retrieve previous symptom checks

## Data Privacy

- Symptom data is stored locally in SQLite database
- No data is shared with third parties
- All processing happens locally (except LLM calls to Google Gemini)

## Limitations & Safety

- **Not a diagnostic tool**: This application does not diagnose medical conditions
- **Educational purpose only**: Results are for learning, not medical decisions
- **LLM limitations**: AI responses may contain inaccuracies
- **Emergency situations**: Always seek immediate care for serious symptoms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is for educational purposes only. It is not intended for clinical use or as a substitute for professional medical advice.

## Contact

For issues or questions, please open an issue in the repository.