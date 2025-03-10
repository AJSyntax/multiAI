import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_option_menu import option_menu

# OpenRouter API URL and Key
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

# Initialize session state variables
if 'user_moods' not in st.session_state:
    st.session_state.user_moods = pd.DataFrame(columns=['date', 'mood', 'context'])
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'streak_count' not in st.session_state:
    st.session_state.streak_count = 0
if 'last_check_in' not in st.session_state:
    st.session_state.last_check_in = None

# Function to generate AI responses using OpenRouter
def generate_response(api_key, mood, context, model="openchat/openchat-7b"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"As a mental health companion, respond to a user who is feeling {mood}.\nTheir context: {context}\nProvide empathetic support and suggest a helpful activity."
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response_data = response.json()
        
        if "choices" in response_data and response_data["choices"]:
            return response_data["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: {response_data.get('error', 'Unknown error')}"
    
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("AJax AI Mental Health Companion 🌟")

# Custom CSS for UI enhancements
st.markdown("""
<style>
.main {
    background-color: #f8f9fa;
}
.stButton>button {
    border-radius: 20px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
.activity-card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Login", "Daily Check-in", "Mood Analytics", "Self-Care", "Gratitude Journal"],
        icons=['person', 'emoji-smile', 'graph-up', 'heart', 'journal'],
        menu_icon="cast",
        default_index=0
    )

# User Authentication
if selected == "Login":
    if not st.session_state.logged_in:
        st.header("Welcome! 👋")
        st.markdown("""
        <style>
        .auth-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        auth_type = st.radio("Choose login type:", ["Email & Password", "Google Sign-In", "Anonymous"])
        
        if auth_type == "Email & Password":
            with st.container():
                st.markdown('<div class="auth-container">', unsafe_allow_html=True)
                username = st.text_input("Email")
                password = st.text_input("Password", type="password")
                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("Login", use_container_width=True):
                        # Simple authentication (replace with secure authentication in production)
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Successfully logged in!")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        elif auth_type == "Google Sign-In":
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            st.info("🔄 Google Sign-In integration coming soon!")
            st.markdown("""<div style='text-align: center'>
                <button style='background-color: #4285f4; color: white; padding: 10px 20px; 
                border: none; border-radius: 5px; cursor: not-allowed; opacity: 0.7'>
                Sign in with Google
                </button></div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.markdown('<div class="auth-container">', unsafe_allow_html=True)
            if st.button("Continue as Guest", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.username = "Guest"
                st.success("Continuing as guest!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.rerun()

# Daily Check-in
elif selected == "Daily Check-in" and st.session_state.logged_in:
    st.header("Daily Mood Check-in 📝")
    
    # Mood selection with emojis
    moods = {
        "Happy 😊": "Happy",
        "Neutral 😐": "Neutral",
        "Sad 😞": "Sad",
        "Anxious 😰": "Anxious",
        "Angry 😡": "Angry",
        "Stressed 😓": "Stressed",
        "Depressed 😔": "Depressed",
        "Motivated 💪": "Motivated",
        "Other ✨": "Other"
    }
    
    selected_mood = st.selectbox(
        "How are you feeling today?",
        list(moods.keys())
    )
    mood = moods[selected_mood]
    
    # Context collection
    context = st.text_area("Would you like to share more about why you feel this way? (Optional)")
    
    if st.button("Submit"):
        # Generate AI response
        ai_response = generate_response(API_KEY, mood, context)
        
        # Store mood data
        new_mood = pd.DataFrame([
            {'date': datetime.now(), 'mood': mood, 'context': context}
        ])
        st.session_state.user_moods = pd.concat([st.session_state.user_moods, new_mood], ignore_index=True)
        
        # Display AI response
        st.success("Thank you for sharing!")
        st.write("💭 AI Response:")
        st.write(ai_response)

# Mood Analytics
elif selected == "Mood Analytics" and st.session_state.logged_in:
    st.header("Mood Analytics 📊")
    
    if not st.session_state.user_moods.empty:
        # Streak tracking
        today = datetime.now().date()
        if st.session_state.last_check_in:
            last_check = st.session_state.last_check_in.date()
            if last_check == today - timedelta(days=1):
                st.session_state.streak_count += 1
            elif last_check != today:
                st.session_state.streak_count = 0
        
        if st.session_state.streak_count > 0:
            st.success(f"🎯 Current Streak: {st.session_state.streak_count} days!")
            if st.session_state.streak_count % 5 == 0:
                st.balloons()
                st.markdown(f"""🎉 **Amazing Achievement!**
                You've maintained a {st.session_state.streak_count}-day streak!
                Keep up the great work on your mental health journey!""")
        
        # Mood distribution
        st.subheader("Mood Distribution")
        mood_counts = st.session_state.user_moods['mood'].value_counts()
        fig_pie = px.pie(values=mood_counts.values, names=mood_counts.index,
                        title='Your Mood Distribution')
        st.plotly_chart(fig_pie)
        
        # Mood trend over time
        st.subheader("Mood Trend Over Time")
        fig_line = px.line(st.session_state.user_moods, x='date', y='mood',
                          title='Your Mood Journey')
        fig_line.update_traces(mode='lines+markers')
        st.plotly_chart(fig_line)
        
        # Weekly patterns
        st.subheader("Weekly Patterns")
        st.session_state.user_moods['day_of_week'] = pd.to_datetime(st.session_state.user_moods['date']).dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_moods = st.session_state.user_moods.groupby('day_of_week')['mood'].agg(list).reindex(day_order)
        
        for day, moods in weekly_moods.items():
            if moods:
                most_common = max(set(moods), key=moods.count)
                st.write(f"**{day}:** Most common mood - {most_common}")
        
        # Insights
        st.subheader("AI Insights")
        most_frequent_mood = mood_counts.index[0]
        st.info(f"📊 Your most frequent mood has been **{most_frequent_mood}**")
        
        if 'Stressed' in mood_counts or 'Anxious' in mood_counts:
            st.markdown("""💡 **Tip:** Consider trying our breathing exercises in the Self-Care section 
            to help manage stress and anxiety.""")
        
        # Mood distribution
        mood_counts = st.session_state.user_moods['mood'].value_counts()
        fig_pie = px.pie(values=mood_counts.values, names=mood_counts.index,
                        title='Mood Distribution')
        st.plotly_chart(fig_pie)
        
        # Recent entries
        st.subheader("Recent Entries")
        st.dataframe(st.session_state.user_moods.tail())
    else:
        st.info("No mood data available yet. Start by doing a daily check-in!")

# Self-Care Activities
elif selected == "Self-Care" and st.session_state.logged_in:
    st.header("Self-Care Activities 🎯")
    
    activities = {
        "2-Minute Breathing Exercise 🫁": {
            "description": "A simple breathing exercise to help you relax and reduce stress.",
            "duration": "2 minutes"
        },
        "Gratitude Journaling 📝": {
            "description": "Write down three things you're grateful for today.",
            "duration": "5 minutes"
        },
        "Quick Physical Activity 🏃‍♂️": {
            "description": "Simple exercises to boost your energy and mood.",
            "duration": "5 minutes"
        },
        "Guided Meditation 🧘‍♂️": {
            "description": "A short meditation session for mental clarity.",
            "duration": "3 minutes"
        }
    }
    
    col1, col2 = st.columns(2)
    
    for i, (activity_name, details) in enumerate(activities.items()):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f'<div class="activity-card">', unsafe_allow_html=True)
            st.subheader(activity_name)
            st.write(details['description'])
            st.caption(f"Duration: {details['duration']}")
            if st.button(f"Start {activity_name.split(' ')[0]}", key=f"activity_{i}"):
                if "Breathing" in activity_name:
                    st.markdown("### Follow the breathing pattern:")
                    for _ in range(3):  # 3 breath cycles
                        st.info("Breathe in... 2... 3... 4")
                        time.sleep(4)
                        st.info("Hold... 2... 3... 4")
                        time.sleep(4)
                        st.info("Breathe out... 2... 3... 4")
                        time.sleep(4)
                elif "Gratitude" in activity_name:
                    st.text_area("What are you grateful for today?", key="gratitude_entry")
                    if st.button("Save Entry", key="save_gratitude"):
                        st.success("Gratitude entry saved!")
                elif "Physical" in activity_name:
                    exercises = [
                        "10 jumping jacks",
                        "10 arm circles",
                        "10 shoulder rolls",
                        "10 knee lifts"
                    ]
                    for ex in exercises:
                        st.write(f"• {ex}")
                elif "Meditation" in activity_name:
                    st.markdown("""🎵 Close your eyes and focus on your breath.
                    Feel the sensation of breathing in and out.
                    Let your thoughts pass by like clouds in the sky.""")
            st.markdown('</div>', unsafe_allow_html=True)

# Gratitude Journal
elif selected == "Gratitude Journal" and st.session_state.logged_in:
    st.header("Gratitude Journal 📖")
    
    st.markdown('<div class="activity-card">', unsafe_allow_html=True)
    today_entry = st.text_area("What are you grateful for today?", height=150)
    if st.button("Save Journal Entry"):
        if today_entry:
            if 'gratitude_entries' not in st.session_state:
                st.session_state.gratitude_entries = []
            st.session_state.gratitude_entries.append({
                'date': datetime.now(),
                'entry': today_entry
            })
            st.success("Journal entry saved! 🌟")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if 'gratitude_entries' in st.session_state and st.session_state.gratitude_entries:
        st.subheader("Past Entries")
        for entry in reversed(st.session_state.gratitude_entries):
            st.markdown(f'<div class="activity-card">', unsafe_allow_html=True)
            st.caption(entry['date'].strftime("%B %d, %Y"))
            st.write(entry['entry'])
            st.markdown('</div>', unsafe_allow_html=True)
        st.write("Follow this simple breathing exercise:")
        st.write("1. Breathe in for 4 seconds")
        st.write("2. Hold for 4 seconds")
        st.write("3. Exhale for 4 seconds")
        st.write("4. Repeat 5 times")
        
    elif activity == "Gratitude Journaling":
        st.write("🌟 Today's Gratitude Prompt:")
        st.write("What's one good thing that happened today?")
        gratitude_entry = st.text_area("Your response:")
        if st.button("Save Entry"):
            st.success("Gratitude entry saved!")
            
    elif activity == "Quick Physical Activity":
        st.write("Try these quick exercises:")
        st.write("1. 10 shoulder rolls")
        st.write("2. 5 gentle neck stretches")
        st.write("3. 10 desk-friendly arm stretches")

else:
    if not st.session_state.logged_in:
        st.warning("Please log in to access this feature.")
