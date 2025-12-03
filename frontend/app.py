import streamlit as st
import requests
import re

# Configuration
API_URL = "http://localhost:9002"

st.set_page_config(page_title="AI Symptom Checker", page_icon="🩺", layout="wide")

# Custom CSS for better cards
st.markdown("""
<style>
    .history-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
    }
    .severity-high { border-left-color: #ff4b4b; }
    .severity-mod { border-left-color: #ffa726; }
    .severity-low { border-left-color: #66bb6a; }
</style>
""", unsafe_allow_html=True)

if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

def login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🩺 AI Symptom Checker")
        st.subheader("Login to your account")
        
        with st.form("login_form"):
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    try:
                        # OAuth2 expects 'username' field, but we send email
                        resp = requests.post(f"{API_URL}/token", data={"username": email, "password": password})
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.token = data["access_token"]
                            st.success("Logged in!")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

def register():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🩺 AI Symptom Checker")
        st.subheader("Create a new account")
        
        with st.form("register_form"):
            username = st.text_input("Username (Display Name)", key="reg_user")
            email = st.text_input("Email Address", key="reg_email")
            password = st.text_input("Password (Min 6 chars)", type="password", key="reg_pass")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                # Client-side validation
                if not username or not email or not password:
                    st.error("All fields are required")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_regex, email):
                        st.error("Invalid email format")
                    else:
                        try:
                            resp = requests.post(f"{API_URL}/register/", json={"username": username, "email": email, "password": password})
                            if resp.status_code == 200:
                                st.success("Registered successfully! Please login.")
                            else:
                                # Parse error detail
                                try:
                                    err = resp.json().get("detail", "Registration failed")
                                    st.error(f"Error: {err}")
                                except:
                                    st.error(f"Error: {resp.text}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")

def delete_history_item(item_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        resp = requests.delete(f"{API_URL}/history/{item_id}", headers=headers)
        if resp.status_code == 200:
            st.success("Deleted successfully")
            st.rerun()
        else:
            st.error("Failed to delete")
    except Exception as e:
        st.error(f"Error: {e}")

def render_history_card(h):
    # Determine severity color/icon
    severity = h.get('severity_estimate', 'Unknown')
    color_class = "severity-low"
    icon = "🟢"
    if "High" in severity:
        color_class = "severity-high"
        icon = "🔴"
    elif "Moderate" in severity:
        color_class = "severity-mod"
        icon = "🟠"

    with st.container():
        st.markdown(f"### 🗓 {h['created_at']}")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**Severity:** {icon} {severity}")
            st.markdown(f"**Summary:** {h['summary']}")
            st.markdown(f"**Symptoms:** _{h['symptoms']}_")
        
        with col2:
            if st.button("🗑️ Delete", key=f"del_{h['id']}"):
                delete_history_item(h['id'])

        with st.expander("📄 View Full Details"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🔍 Possible Causes")
                for c in h.get('possible_common_causes', []):
                    st.write(f"- {c}")
                
                st.markdown("#### 💡 Advice")
                for t in h.get('self_care_tips', []):
                    st.write(f"- {t}")
            
            with c2:
                st.markdown("#### 🚩 Red Flags")
                for f in h.get('red_flags', []):
                    st.error(f"- {f}")
            
        st.divider()

def main_app():
    # Fetch user info if not present (to get username)
    if not st.session_state.username:
        # We can decode token or just rely on a profile endpoint if we had one.
        # Since we don't have a /me endpoint, we can decode the JWT locally or add /me.
        # For now, let's just show "Welcome" without username or decode if possible.
        # Actually, let's add a quick /me endpoint in backend or just parse the token.
        # Parsing token in python without key is possible for payload.
        try:
            import base64
            import json
            token = st.session_state.token
            # Simple decode without verify (backend verifies)
            payload = token.split(".")[1]
            padded = payload + '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(padded).decode()
            user_data = json.loads(decoded)
            st.session_state.username = user_data.get("sub", "User")
        except:
            st.session_state.username = "User"

    with st.sidebar:
        st.title("🩺 AI Health")
        st.write(f"Welcome, **{st.session_state.username}**!")
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
    
    tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "🔍 Check Symptoms", "📜 History"])
    
    # --- DASHBOARD ---
    with tab1:
        st.title("Dashboard")
        st.markdown(f"### 👋 Welcome, {st.session_state.username}!")
        st.info("Use the 'Check Symptoms' tab to get an AI analysis of your condition.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🚀 Quick Actions")
            st.write("Start a new analysis to get instant feedback.")
        
        with col2:
            st.markdown("#### 📊 Recent Activity")
            # Fetch latest 1 item for preview
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                resp = requests.get(f"{API_URL}/history/", headers=headers)
                if resp.status_code == 200:
                    history = resp.json()
                    if history:
                        latest = history[0]
                        st.write(f"**Last Check:** {latest['created_at']}")
                        st.write(f"**Summary:** {latest['summary']}")
                    else:
                        st.write("No recent activity.")
            except:
                st.write("Could not load recent activity.")

    # --- CHECK SYMPTOMS ---
    with tab2:
        st.header("Check Symptoms")
        symptoms = st.text_area("Describe your symptoms:", height=150, placeholder="e.g., I have a headache and sore throat for two days.")
        
        if st.button("Analyze Symptoms", type="primary"):
            if not symptoms:
                st.warning("Please enter symptoms.")
                return
            
            with st.spinner("Analyzing..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    resp = requests.post(f"{API_URL}/check_symptoms/", json={"symptoms": symptoms}, headers=headers)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        
                        # Display Results
                        st.success("Analysis Complete")
                        
                        st.subheader("📝 Summary")
                        st.write(data["summary"])
                        
                        st.subheader("🎯 Severity Estimate")
                        severity = data["severity_estimate"]
                        if "High" in severity:
                            st.error(f"**{severity}**")
                        elif "Moderate" in severity:
                            st.warning(f"**{severity}**")
                        else:
                            st.success(f"**{severity}**")
                            
                        c1, c2 = st.columns(2)
                        with c1:
                            st.subheader("🔍 Possible Causes")
                            for cause in data["possible_common_causes"]:
                                st.write(f"- {cause}")
                        with c2:
                            st.subheader("💡 Self-Care Tips")
                            for tip in data["self_care_tips"]:
                                st.write(f"- {tip}")
                            
                        st.subheader("🚩 Red Flags")
                        for flag in data["red_flags"]:
                            st.error(f"- {flag}")
                            
                        st.info(f"📅 **Consultation:** {data['consultation_timing']}")
                        
                        st.divider()
                        st.caption(f"⚠️ **Disclaimer**: {data['disclaimer']}")
                        
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- HISTORY ---
    with tab3:
        st.header("📜 Consultation History")
        if st.button("Refresh History"):
            st.rerun()
            
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            resp = requests.get(f"{API_URL}/history/", headers=headers)
            if resp.status_code == 200:
                history = resp.json()
                if not history:
                    st.info("No history found.")
                for h in history:
                    render_history_card(h)
            else:
                st.error("Failed to load history")
        except Exception as e:
            st.error(f"Error loading history: {e}")

# Router
if not st.session_state.token:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login()
    with tab2:
        register()
else:
    main_app()
