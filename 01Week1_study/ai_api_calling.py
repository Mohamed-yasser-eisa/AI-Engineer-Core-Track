#Running my first AI API call
import os
import sys
import json
from dotenv import load_dotenv
from anthropic import Anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '00Course_Materials', 'week1'))
from scraper import fetch_website_contents  # type: ignore[import]


#-------------------------------------------------------------------------------------------------------
# Load environment variables from .env
load_dotenv(override=True)
my_api_key = os.getenv('ANTHROPIC_API_KEY')

#Check the key:
if not my_api_key:
    print("❌ANTHROPIC_API_KEY not found in environment variables.")
else:
    print("✅ANTHROPIC_API_KEY found in environment variables.")
#-------------------------------------------------------------------------------------------------------
# Now let's make a quick call to the frontier model:
message = "Hello Claude code, what is my name?"
messages = [{
    "role": "user",
     "content": message
}]
print(messages)
# Create an instance from anthropic object, passing the key explicitly
claude_code = Anthropic(api_key=my_api_key)
#now let's start the first API call:
response = claude_code.messages.create(max_tokens=500, messages=messages, model="claude-sonnet-4-6")

print(response.content[0].text)
#-------------------------------------------------------------------------------------------------------

# fetched_web_data = fetch_website_contents("https://www.anthropic.com/news/claude-3-5-sonnet")
# print(fetched_web_data)

#update the system prompt of the AI, so we can control the "context" of the question and answer:
system_prompt = "You are a helpful assistant that analysis the content of a website and provide a short summary ignoring text that might be navigation related. \
Respont in markdown. And don't wrap the markdown in a code block - response just with the markdown."
user_prefix_prompt = "Here are the content of the website, if it contains news or announcements, then summarize them too."


def generate_ai_message(website_content):
    ai_messages = [
    {"role": "user", "content": user_prefix_prompt+website_content}
    ]
    return ai_messages

def ai_summarize_web_url(url):
    website_content = fetch_website_contents(url)
    ai_messages = generate_ai_message(website_content)
    # Reuse the key here as well
    client = Anthropic(api_key=my_api_key)
    response = client.messages.create(
        max_tokens=500,
        system=system_prompt,
        messages=ai_messages,
        model="claude-sonnet-4-6"
    )
    return response.content[0].text


result = ai_summarize_web_url("https://github.com/ed-donner/llm_engineering")
print(result)
