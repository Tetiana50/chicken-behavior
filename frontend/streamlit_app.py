import streamlit as st
import requests
import time
from pathlib import Path

# API Configuration
API_URL = "http://localhost:8000/api/v1"

def upload_video(file, title, description, frame_interval):
    files = {"file": file}
    params = {"title": title, "description": description, "frame_interval": frame_interval}
    try:
        response = requests.post(f"{API_URL}/videos/upload", files=files, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to upload video: {str(e)}")
    print("response")
    print(response.json())
    return response.json()

def process_youtube_video(url, title, description, frame_interval):
    data = {
        "title": title,
        "description": description,
        "source": "youtube",
        "youtube_url": url,
        "frame_interval": frame_interval
    }
    response = requests.post(f"{API_URL}/videos/youtube", json=data)
    return response.json()

def get_video_status(video_id):
    response = requests.get(f"{API_URL}/videos/{video_id}/status")
    return response.json()

def get_video_frames(video_id):
    response = requests.get(f"{API_URL}/videos/{video_id}/frames")
    return response.json()

def analyze_frames(video_id, frame_ids, sequence_prompt, description, messages):
    data = {
        "video_id": video_id,
        "frame_ids": frame_ids,
        "analysis_type": "default",
        "sequence_prompt": sequence_prompt,
        "description": description,
        "messages": messages
    }
    print("data", data)
    response = requests.post(f"{API_URL}/frames/analyze", json=data)
    return response.json()

# Streamlit UI
st.title("Video Processing Dashboard")

# Sidebar
st.sidebar.title("Upload Options")
upload_option = st.sidebar.radio(
    "Choose upload method:",
    ("Upload Video File", "YouTube URL")
)
# Add frame interval selection
frame_interval = st.sidebar.number_input(
    "Select frame interval (seconds)",
    min_value=1,
    max_value=30,
    value=10,
    help="Extract one frame every X seconds"
)

# Store frame interval in session state to use during processing
st.session_state.frame_interval = frame_interval

if upload_option == "Upload Video File":
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])
    if uploaded_file:
        title = st.text_input("Video Title", uploaded_file.name)
        description = st.text_area("Description", "")
        
        if st.button("Process Video"):
            with st.spinner("Uploading and processing video..."):
                try:
                    print("uploading video")
                    print("uploaded_file", uploaded_file)
                    print("title", title)
                    print("description", description)
                    result = upload_video(uploaded_file, title, description, st.session_state.frame_interval)
                    st.session_state.video_id = result["id"]
                    st.success("Video uploaded successfully!")
                except Exception as e:
                    st.error(f"Error uploading video: {str(e)}")

else:  # YouTube URL
    youtube_url = st.text_input("Enter YouTube URL", value="https://www.youtube.com/watch?v=9RQ8r2fI-D0")
    if youtube_url:
        title = st.text_input("Video Title", "YouTube Video")
        description = st.text_area("Description", "Курчата")
        
        if st.button("Process Video"):
            with st.spinner("Processing YouTube video..."):
                try:
                    result = process_youtube_video(youtube_url, title, description, st.session_state.frame_interval)
                    st.session_state.video_id = result["id"]
                    st.success("YouTube video processing started!")
                except Exception as e:
                    st.error(f"Error processing YouTube video: {str(e)}")


# Display processing status and frames
if "video_id" in st.session_state:
    st.header("Processing Status")
    status = get_video_status(st.session_state.video_id)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Update progress
    progress = status["progress"] / 100
    progress_bar.progress(progress)
    status_text.text(f"Status: {status['status']} - {status['message']}")
    
    if status["status"] == "completed":
        st.header("Extracted Frames")
        frames = get_video_frames(st.session_state.video_id)

        # Display frames in a grid
        cols = st.columns(4)
        for idx, frame_path in enumerate(frames):
            with cols[idx % 4]:
                st.image(frame_path, caption=f"Frame {idx + 1}")
        
        # Initialize chat history in session state if it doesn't exist
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask me anything about this video..."):
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing ..."):
                    frame_ids = [Path(frame).stem.split("_")[1] for frame in frames]
                    analysis_results = analyze_frames(st.session_state.video_id, frame_ids, prompt, description, st.session_state.messages)
                    
                    if analysis_results.get("status") == "success":
                        analysis_text = analysis_results["sequence_analysis"]
                        st.write(analysis_text)
                        # Add assistant response to history
                        st.session_state.messages.append({"role": "assistant", "content": analysis_text})
                    else:
                        error_message = f"Analysis failed: {analysis_results.get('error', 'Unknown error')}"
                        st.error(error_message)
                        # Add error message to history
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
        
        # Add a button to clear chat history
        if len(st.session_state.messages) > 0:
            if st.button("Clear Chat History", key="clear_chat"):
                # Clear the messages from session state
                st.session_state.messages = []
                
                # Display the previous chat history with a "Cleared" indicator
                st.info("Chat history has been cleared")
                
                # Force a rerun to start fresh
                st.rerun()

