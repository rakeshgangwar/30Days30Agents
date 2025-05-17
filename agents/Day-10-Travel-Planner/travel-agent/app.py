import os
import asyncio
import gradio as gr
from datetime import datetime
from agent import TravelAgent

# Initialize the travel agent
def initialize_agent():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Error: OPENAI_API_KEY environment variable is not set!")
    return TravelAgent(openai_api_key=openai_api_key)

# Create a global agent instance
try:
    agent = initialize_agent()
except ValueError as e:
    print(str(e))
    print("Please set your OPENAI_API_KEY environment variable or create a .env file.")
    agent = None

# Chat functionality
async def chat_response(history):
    """Process a user message and return the agent's response."""
    if agent is None:
        return history + [{"role": "assistant", "content": "Error: TravelAgent could not be initialized. Please check your API keys."}]
    
    # Extract the user's message from history - should be the last message with role "user"
    user_message = ""
    for msg in reversed(history):
        if msg["role"] == "user":
            user_message = msg["content"]
            break
    
    # If we couldn't find a user message, return an error
    if not user_message:
        return history + [{"role": "assistant", "content": "I couldn't understand your message. Please try again."}]
    
    # Process the user message
    response = await agent.chat(user_message)
    
    # Return updated history with bot response
    return history + [{"role": "assistant", "content": response}]

# Itinerary generation functionality
async def generate_itinerary(
    from_location, 
    to_location, 
    start_date, 
    end_date, 
    budget, 
    transportation,
    accommodation_type,
    interests,
    num_travelers
):
    """Generate a travel itinerary based on user inputs."""
    if agent is None:
        return "Error: TravelAgent could not be initialized. Please check your API keys."
    
    # Format interests as a list
    interest_list = [interest.strip() for interest in interests.split(",")]
    
    # Create the request data
    request_data = {
        "from_location": from_location,
        "to_location": to_location,
        "start_date": start_date,
        "end_date": end_date,
        "number_of_travelers": num_travelers,
        "preferences": {
            "budget": budget,
            "transportation": transportation,
            "accommodation_type": accommodation_type,
            "interests": interest_list
        }
    }
    
    # Generate the itinerary
    result = await agent.generate_itinerary(request_data)
    
    # Return the formatted itinerary
    return result["itinerary"]

# Create the Gradio interface
with gr.Blocks(title="TravelBuddy - AI Travel Assistant") as demo:
    gr.Markdown("# TravelBuddy - AI Travel Assistant")
    gr.Markdown("Ask travel questions or generate a detailed travel itinerary.")
    
    with gr.Tab("Chat"):
        gr.Markdown("### Chat with TravelBuddy")
        gr.Markdown("Ask any travel-related questions and get personalized assistance.")
        
        chatbot = gr.Chatbot(height=400, type="messages")
        msg = gr.Textbox(label="Your message", placeholder="Ask me anything about travel...")
        clear = gr.Button("Clear conversation")
        
        # Set up chat functionality
        msg.submit(
            fn=lambda message, history: (None, history + [{"role": "user", "content": message}]),
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False
        ).then(
            fn=chat_response,  # Use the async function directly
            inputs=chatbot,  # Only pass the chatbot history
            outputs=chatbot,
            queue=True
        )
        
        clear.click(lambda: None, None, chatbot, queue=False)
    
    with gr.Tab("Generate Itinerary"):
        gr.Markdown("### Generate a Travel Itinerary")
        gr.Markdown("Fill in the details below to create a personalized travel plan.")
        
        with gr.Row():
            with gr.Column():
                from_location = gr.Textbox(label="From Location", placeholder="e.g., New York")
                to_location = gr.Textbox(label="To Location", placeholder="e.g., San Francisco")
                
                with gr.Row():
                    start_date = gr.Textbox(label="Start Date (YYYY-MM-DD)", placeholder="e.g., 2024-07-01")
                    end_date = gr.Textbox(label="End Date (YYYY-MM-DD)", placeholder="e.g., 2024-07-05")
                
                num_travelers = gr.Slider(minimum=1, maximum=10, value=2, step=1, label="Number of Travelers")
                
            with gr.Column():
                budget = gr.Radio(
                    choices=["budget", "medium", "luxury"], 
                    label="Budget", 
                    value="medium"
                )
                
                transportation = gr.Radio(
                    choices=["car", "public", "flight", "mixed"], 
                    label="Transportation Preference", 
                    value="mixed"
                )
                
                accommodation_type = gr.Radio(
                    choices=["hotel", "hostel", "apartment", "resort"], 
                    label="Accommodation Type", 
                    value="hotel"
                )
                
                interests = gr.Textbox(
                    label="Interests (comma-separated)", 
                    placeholder="e.g., food, culture, nature, history, art"
                )
        
        generate_btn = gr.Button("Generate Itinerary", variant="primary")
        itinerary_output = gr.Textbox(label="Your Itinerary", lines=20)
        
        # Set up itinerary generation functionality
        generate_btn.click(
            fn=generate_itinerary,
            inputs=[
                from_location, to_location, start_date, end_date, 
                budget, transportation, accommodation_type, interests, num_travelers
            ],
            outputs=itinerary_output
        )

# Launch the app
if __name__ == "__main__":
    demo.queue()
    demo.launch(share=True)
