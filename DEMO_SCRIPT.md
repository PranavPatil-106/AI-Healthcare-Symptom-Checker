# Healthcare Symptom Checker - Demo Script

## Introduction (0:00-0:30)

Hello and welcome to the demonstration of the Healthcare Symptom Checker, an innovative application that combines the power of FastAPI and Streamlit with advanced LLM technology to provide educational medical insights.

This tool is designed to help users understand possible conditions based on their symptoms, while emphasizing that it's for educational purposes only and not a substitute for professional medical advice.

## Application Overview (0:30-1:00)

Let me show you the main interface. As you can see, we have a clean, intuitive design with clear medical disclaimer prominently displayed. The application has two main tabs: Symptom Checker and History.

On the left sidebar, we provide clear instructions on how to use the tool effectively.

## Technical Architecture (1:00-1:30)

Behind the scenes, we have a robust FastAPI backend that handles all the business logic and integrates with OpenAI's GPT models. The frontend is built with Streamlit for a responsive user experience.

Data is stored locally in a SQLite database, ensuring privacy and compliance with data protection regulations.

## Live Demonstration (1:30-3:30)

Let's go through a live demonstration:

1. First, I'll describe some symptoms in the text area. For example: "I've had a persistent headache for three days, accompanied by sensitivity to light and mild nausea."

2. Now I'll click the "Check Symptoms" button. As you can see, the application is analyzing the symptoms using the LLM.

3. Here are the results! The application has identified possible conditions with likelihood assessments. We can see Migraine as a high likelihood condition with a detailed description and recommended next steps.

4. Let's expand another condition to see more details.

5. Notice the comprehensive disclaimer reminding users this is for educational purposes only.

6. Now let's check the History tab to see our previous queries. As you can see, our symptom check has been recorded with timestamp.

## Key Features Highlight (3:30-4:00)

Some standout features of this application include:

- AI-powered analysis with LLM integration
- Comprehensive safety disclaimers throughout
- Local data storage for privacy
- Intuitive user interface with expandable sections
- Query history for reference

## Conclusion (4:00-4:30)

In conclusion, the Healthcare Symptom Checker demonstrates how modern web technologies can be combined with AI to create educational tools that help people understand health information. Remember, this tool emphasizes safety and education, never replacing professional medical consultation.

Thank you for watching this demonstration. For more information, please refer to the comprehensive README file in the repository.

## Setup Instructions (for reference)

To run this application yourself:
1. Install dependencies with pip install -r requirements.txt
2. Set your OpenAI API key in the .env file
3. Start the backend with python backend/main.py
4. Start the frontend with streamlit run frontend/app.py