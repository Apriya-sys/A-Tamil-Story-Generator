import streamlit as st
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO

# Initialize OpenAI client with Together.ai base URL
client = OpenAI(
    api_key=st.secrets['TOGETHER_API_KEY'],
    base_url="https://api.together.xyz/v1"
)

def generate_image(prompt: str):
    """Generate an image using FLUX model and return both image and URL"""
    try:
        response = client.images.generate(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt=prompt,
        )
        # Get image URL from response
        image_url = response.data[0].url
        
        # Load image and return both image and URL
        response = requests.get(image_url)
        return Image.open(BytesIO(response.content)), image_url
    except Exception as e:
        st.error(f"Failed to generate image: {str(e)}")
        return None, None

def generate_story_outline(topic: str, num_paragraphs: int):
    """Generate a story outline with multiple paragraph prompts"""
    try:
        prompt = f"""Create {num_paragraphs} different scene descriptions for a story about {topic} set in Andhra Pradesh, India. 
        Each scene should be unique and flow together to tell a coherent story.
        Format: Return only the numbered list of scene descriptions, one per line."""
        
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # Split the response into separate scenes
        scenes = response.choices[0].message.content.strip().split('\n')
        return [scene.strip() for scene in scenes if scene.strip()]
    except Exception as e:
        st.error(f"Failed to generate story outline: {str(e)}")
        return None

def generate_paragraph(image_url: str, scene_description: str, paragraph_number: int):
    """Generate a single paragraph using Llama model with the image URL"""
    try:
        prompt = f"""Look at this image: {image_url}. 
        Write a detailed paragraph for part {paragraph_number} of the story based on this scene: {scene_description} in Telugu.
        Make sure it flows well with the overall narrative."""
        
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Failed to generate paragraph: {str(e)}")
        return None

# Main app
st.title("🌟Story Generator in Telugu")
st.write("Generate a story with multiple scenes and images set in Andhra Pradesh!")

# Sidebar for sample examples
st.sidebar.header("Sample Examples")
st.sidebar.write("Here are some example topics you can use:")

# List of sample topics
sample_topics = [
    "A magical adventure in a forest",
    "A journey through space",
    "A detective story in a bustling city",
    "A historical tale set in ancient India",
    "A fantasy world with mythical creatures",
    "An underwater exploration of a lost city",
    "A time travel adventure to the Renaissance",
    "A quest to find a hidden treasure",
    "A superhero saving the day in a small town",
    "A love story set in a bustling marketplace",
    "A thrilling escape from a haunted mansion",
    "A journey through a mystical desert",
    "A battle between good and evil in a fantasy realm",
    "A coming-of-age story in a small village",
    "A culinary adventure around the world",
    "A race against time to save the planet",
    "A magical school for young wizards",
    "An epic quest to find a lost artifact",
    "A rivalry between two kingdoms",
    "A mysterious disappearance in a small town",
    "A journey through the vibrant streets of Hyderabad",
    "A tale of friendship in a small village",
    "An adventure in the hills of Araku Valley",
    "A story of love blossoming during a festival",
    "A quest to uncover ancient secrets in Amaravati",
    "A thrilling chase through the markets of Visakhapatnam",
    "A magical encounter with a sage in Tirupati",
    "A journey to the historic ruins of Hampi",
]

# Create buttons for each sample topic
for topic in sample_topics:
    if st.sidebar.button(topic):
        st.session_state.topic = topic  # Store the selected topic in session state

# Get user input
topic = st.text_input("What's your story about?", placeholder="e.g., A magical adventure in a forest", value=st.session_state.get('topic', ''))
# Remove language selection and set to Telugu
language = "Telugu"  # Set language to Telugu directly
# Remove the slider and set a fixed number of paragraphs
num_paragraphs = 5  # Fixed to 5 paragraphs

# Generate button
if st.button("Generate Story", type="primary"):
    if topic:
        with st.spinner("Creating your story..."):
            # Generate story outline first
            scene_descriptions = generate_story_outline(topic, num_paragraphs)  # No language parameter
            
            if scene_descriptions:
                # Create story container
                story_container = st.container()
                
                with story_container:
                    st.write("## Your Story")
                    
                    # Generate each scene with image and paragraph
                    for i, scene in enumerate(scene_descriptions, 1):
                        
                        # Generate image for this scene using the scene description
                        image, image_url = generate_image(f"A scene depicting: {scene} in Andhra Pradesh")  # Updated prompt
                        
                        if image and image_url:
                            # Display image
                            st.image(image, caption=f"Scene {i}")
                            
                            # Generate and display paragraph
                            paragraph = generate_paragraph(image_url, scene, i)  # No language parameter
                            if paragraph:
                                st.write(paragraph)
                            
                            # Add spacing between scenes
                            st.write("---")
    else:
        st.warning("Please enter a topic first!")

