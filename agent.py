import streamlit as st
import requests

# OpenRouter API URL
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Function to generate content using OpenRouter
def generate_content(api_key, prompt, model="openchat/openchat-7b"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
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
st.title("Multi-Agent AI")

# User inputs API Key
api_key = st.text_input("Enter your OpenRouter API key", type="password")

# User inputs query/topic
topic = st.text_area("Enter a topic")

if st.button("Generate"):
    if not api_key or not topic:
        st.error("Please provide both an API key and a topic.")
    else:
        with st.spinner("Generating content..."):
            # Agent 1: Blog Article
            blog_prompt = f"Write a short blog article on the topic: {topic}. Make it informative and engaging."
            blog_article = generate_content(api_key, blog_prompt)

            # Agent 2: Social Media Posts
            social_prompt = f"Create 3 engaging social media posts about {topic}. Each post should be concise, attention-grabbing, and suitable for platforms like Twitter, Instagram, and Facebook."
            social_posts = generate_content(api_key, social_prompt)

            # Agent 3: Short Story
            story_prompt = f"Write a short fictional story based on the topic: {topic}. It should be creative, engaging, and under 200 words."
            short_story = generate_content(api_key, story_prompt)

        # Display results
        st.subheader("📄 Blog Article")
        st.write(blog_article)

        st.subheader("📢 Social Media Posts")
        st.write(social_posts)

        st.subheader("📖 Short Story")
        st.write(short_story)
