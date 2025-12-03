import streamlit as st
import requests
import json
import time

# Streamlit app configuration
st.set_page_config(
    page_title="Healthcare Symptom Checker",
    page_icon="🏥",
    layout="wide"
)

# App title and description
st.title("🏥 Healthcare Symptom Checker")
st.markdown("""
*This tool provides educational information only and is not a substitute for professional medical advice.*
*Always consult with a qualified healthcare provider for diagnosis and treatment.*
""")

# Sidebar with information
st.sidebar.header("About this tool")
st.sidebar.info("""
This symptom checker uses advanced AI to analyze your symptoms and provide possible conditions 
along with recommended next steps. Remember, this is for educational purposes only.
""")

st.sidebar.header("How to use")
st.sidebar.markdown("""
1. Describe your symptoms in detail
2. Click "Check Symptoms"
3. Review the possible conditions
4. Follow the recommended next steps
""")

# API endpoint configuration
API_URL = "http://localhost:8080/check_symptoms/"
HISTORY_URL = "http://localhost:8080/history/"

# Create tabs for symptom checking and history
tab1, tab2 = st.tabs(["Symptom Checker", "History"])

with tab1:
    # Main symptom input area
    st.header("Describe Your Symptoms")
    symptoms = st.text_area(
        "Please describe your symptoms in detail:",
        height=150,
        placeholder="Example: I've had a headache for 3 days, accompanied by a mild fever and fatigue..."
    )

    # Check symptoms button
    if st.button("Check Symptoms", type="primary"):
        if symptoms.strip():
            with st.spinner("Analyzing your symptoms..."):
                try:
                    # Call the backend API
                    response = requests.post(
                        API_URL,
                        json={"symptoms": symptoms},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display results
                        st.success("Analysis complete!")
                        
                        # Show disclaimer
                        st.warning(data["disclaimer"])
                        
                        # Display possible conditions
                        st.header("Possible Conditions")
                        
                        for i, condition in enumerate(data["possible_conditions"], 1):
                            with st.expander(f"{i}. {condition['condition']} ({condition['likelihood']} Likelihood)", expanded=True):
                                st.markdown(f"**Description:** {condition['description']}")
                                st.markdown("**Recommended Next Steps:**")
                                for step in condition["next_steps"]:
                                    st.markdown(f"- {step}")
                    else:
                        st.error(f"Error: Received status code {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend service. Please ensure the API is running on http://localhost:8080")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    # Fallback to mock data in case of error
                    st.info("Showing example data while we fix the connection:")
                    
                    # Mock API response
                    mock_response = {
                        "symptoms": symptoms,
                        "possible_conditions": [
                            {
                                "condition": "Common Cold",
                                "description": "A viral infection of your nose and throat (upper respiratory tract).",
                                "likelihood": "High",
                                "next_steps": [
                                    "Rest and stay hydrated",
                                    "Use over-the-counter cold medications",
                                    "Monitor symptoms for 2-3 days"
                                ]
                            },
                            {
                                "condition": "Allergic Rhinitis",
                                "description": "An allergic response causing inflammation of the nasal airways.",
                                "likelihood": "Medium",
                                "next_steps": [
                                    "Identify and avoid allergens",
                                    "Consider antihistamines",
                                    "Consult a doctor if symptoms persist"
                                ]
                            },
                            {
                                "condition": "Influenza (Flu)",
                                "description": "A common infectious disease caused by influenza viruses.",
                                "likelihood": "Low",
                                "next_steps": [
                                    "Rest and increase fluid intake",
                                    "Take fever reducers if needed",
                                    "Seek immediate care if difficulty breathing"
                                ]
                            }
                        ],
                        "disclaimer": "DISCLAIMER: This tool provides educational information only and is not a substitute for professional medical advice. Always consult with a qualified healthcare provider for diagnosis and treatment. Results are based on general medical knowledge and may not apply to your specific situation."
                    }
                    
                    # Show disclaimer
                    st.warning(mock_response["disclaimer"])
                    
                    # Display possible conditions
                    st.header("Possible Conditions")
                    
                    for i, condition in enumerate(mock_response["possible_conditions"], 1):
                        with st.expander(f"{i}. {condition['condition']} ({condition['likelihood']} Likelihood)", expanded=True):
                            st.markdown(f"**Description:** {condition['description']}")
                            st.markdown("**Recommended Next Steps:**")
                            for step in condition["next_steps"]:
                                st.markdown(f"- {step}")
        else:
            st.error("Please describe your symptoms before clicking 'Check Symptoms'.")

with tab2:
    st.header("Recent Symptom Checks")
    st.markdown("View your recent symptom checks and their results.")
    
    try:
        # Fetch history from backend
        response = requests.get(HISTORY_URL, timeout=10)
        
        if response.status_code == 200:
            history_data = response.json()
            
            if history_data:
                for item in history_data:
                    with st.expander(f"Check #{item['id']} - {item['created_at'][:19].replace('T', ' ')}"):
                        st.write(f"**Symptoms:** {item['symptoms']}")
            else:
                st.info("No history available yet. Check some symptoms to see them appear here!")
        else:
            st.error("Failed to load history. Please try again later.")
            
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend service. Please ensure the API is running.")
    except Exception as e:
        st.error(f"An error occurred while loading history: {str(e)}")

# Footer
st.markdown("---")
st.caption("⚠️ This tool is for educational purposes only. Always seek professional medical advice.")