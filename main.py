"""
LangChain Chatbot Script

This script demonstrates how to use the LangChain package to create a chatbot 
that interacts with multiple language models sequentially and sends the 
conversation history to the PERSONAL_AI memory stack. 

The script follows these steps:

1. Set up the necessary dependencies and API tokens.
2. Define a list of model names to be used in the LangChain.
3. Create LLMChain objects for each model name, initializing them with the HuggingFaceHub and PromptTemplate objects.
4. Prompt the user for a question.
5. Iterate through each model in the LLMChain and generate responses using LangChain.
6. Send the user's question and the generated responses to the PERSONAL_AI Message API for further processing.
7. Convert the conversation history and responses to a JSONL-formatted string.
8. Create a memory with the conversation history and responses using the PERSONAL_AI Memory API.
9. Print the result of creating the memory or handle any errors.

Author: Matthew Schafer
Date: 2023-June-05
"""

# Import necessary libraries and modules
import os
from datetime import datetime
import json
from langchain import HuggingFaceHub, LLMChain, PromptTemplate
import requests

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Hugging Face Hub LLM
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["PERSONAL_AI_API_KEY"] = os.getenv("PERSONAL_AI_API_KEY")

# List of model names
model_names = [
    "gpt2",
    "gpt2-medium",
    "gpt2-large",
    "gpt2-xl",
    "gpt3.5-turbo",
    "bert-base-uncased",
    "bert-large-uncased",
    "roberta-base",
    "roberta-large",
    "distilbert-base-uncased",
    "distilbert-base-uncased-distilled-squad",
    "gpt-neo-125M",
    "gpt-neo-1.3B",
    "gpt-neo-2.7B",
    "mosaicml/mpt-7b-storywriter",
    "mosaicml/mpt-7b-chat",
    "mosaicml/mpt-7b-instruct",
    "mosaicml/mpt-7b"
]

# Loop through model names and create LLMChain for each
llm_chains = {}
for model_name in model_names:
    HUB_LLM = HuggingFaceHub(repo_id=model_name, model_kwargs={"temperature": 0, "max_length": 64})
    TEMPLATE= """User: {user_input}\nBot: """
    PROMPT = PromptTemplate(TEMPLATE=TEMPLATE, input_variables=['user_input'])
    llm_chains[model_name] = LLMChain(PROMPT=PROMPT, llm=HUB_LLM)

# Ask a user question
user_question = input("Enter your question: ")

# Initialize the conversation history
conversation_history = user_question

# Store all responses
responses = []

# Iterate through each model in the LLM chain
for model_name, llm_chain in llm_chains.items():
    print(f"\nInteracting with {model_name}...")
    user_input = conversation_history

    # Generate the response using LangChain
    langchain_response = llm_chain.run(user_input)
    print(f"Bot {model_name}: {langchain_response}")

    # Append the response to the list of responses
    responses.append((model_name, langchain_response))

# Create the payload for PERSONAL_AI Message API
payload = {
    "Text": user_question,
    "Context": json.dumps(responses)
}

# Make a POST request to the PERSONAL_AI Message API
url = "https://api.personal.ai/v1/message"
headers = {
    "Content-Type": "application/json",
    "x-api-key": PERSONAL_AI_API_KEY
}
print("Sending user question and responses to PERSONAL_AI Message API...")
response = requests.post(url, headers=headers, json=payload, timeout=30)

# Process the response from PERSONAL_AI Message API
if response.status_code == 200:
    message_data = response.json()
    ai_message = message_data.get("ai_message")
    ai_score = message_data.get("ai_score")
    print("AI Message:", ai_message)
    print("AI Score:", ai_score)
else:
    print("Failed to send message to PERSONAL_AI:", response.text)

# Convert conversation history and responses to JSONL-formatted string
JSONL_STRING = ""
for response in responses:
    model_name, response_text = response
    JSONL_STRING += json.dumps({
        "user_question": user_question,
        "model_name": model_name,
        "response": response_text
    }) + "\n"

# Create a memory with the conversation history and responses
MEMORY_API_URL = "https://api.personal.ai/v1/memory"
MEMORY_PAYLOAD = {
    "Text": JSONL_STRING,
    "SourceName": "Conversation History",
    "CreatedTime": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z"),
    "DeviceName": "Laptop"
}

# Make a POST request to create a memory with the conversation history and responses
print("Creating memory with conversation history and responses...")
response = requests.post(
    MEMORY_API_URL,
    headers={"Content-Type": "application/json", "x-api-key": PERSONAL_AI_API_KEY},
    json=MEMORY_PAYLOAD,
    timeout=30  # Set the timeout to 30 seconds instead of the default 1
)

if response.status_code == 200:
    memory_data = response.json()
    # Process the response data as needed
    print("Memory created successfully:", memory_data)
else:
    print("Failed to create memory:", response.text)

# End of script
