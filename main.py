import requests
import json
from getpass import getpass
import os
from datetime import datetime
from langchain import HuggingFaceHub, LLMChain, PromptTemplate

# Set up Hugging Face Hub LLM
HUGGINGFACEHUB_API_TOKEN = getpass()
PERSONAL_AI_API_KEY = getpass()
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
os.environ["PERSONAL_AI_API_KEY"] = PERSONAL_AI_API_KEY


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
    hub_llm = HuggingFaceHub(repo_id=model_name, model_kwargs={"temperature": 0, "max_length": 64})
    template = """User: {user_input}\nBot: """
    prompt = PromptTemplate(template=template, input_variables=['user_input'])
    llm_chains[model_name] = LLMChain(prompt=prompt, llm=hub_llm)

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
response = requests.post(url, headers=headers, json=payload)

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
jsonl_string = ""
for response in responses:
    model_name, response_text = response
    jsonl_string += json.dumps({
        "user_question": user_question,
        "model_name": model_name,
        "response": response_text
    }) + "\n"

# Create a memory with the conversation history and responses
memory_api_url = "https://api.personal.ai/v1/memory"
memory_payload = {
    "Text": jsonl_string,
    "SourceName": "Conversation History",
    "CreatedTime": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z"),
    "DeviceName": "Macbook Pro"
}

# Make a POST request to create a memory with the conversation history and responses
response = requests.post(
    memory_api_url,
    headers={"Content-Type": "application/json", "x-api-key": PERSONAL_AI_API_KEY},
    json=memory_payload,
    timeout=30  # Set the timeout to 30 seconds instead of the default 1
)

if response.status_code == 200:
    memory_data = response.json()
    # Process the response data as needed
    print("Memory created successfully:", memory_data)
else:
    print("Failed to create memory:", response.text)

# End of script
