import os
import sys
import json
from dotenv import load_dotenv
from anthropic import Anthropic

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '00Course_Materials', 'week1'))
from scraper import fetch_website_contents  # type: ignore[import]

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv(override=True)
my_api_key = os.getenv('ANTHROPIC_API_KEY')

if not my_api_key:
    print("ANTHROPIC_API_KEY not found in environment variables.")
else:
    print("ANTHROPIC_API_KEY found in environment variables.")

# ---------------------------------------------------------------------------
# System prompt — Valeo Visibility OEM Customer Analysis Agent
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """
You are an expert automotive business analyst working for Valeo's Visibility Systems division.
Your role is to analyze OEM (Original Equipment Manufacturer) customers in the context of
new LED lighting technology projects for passenger cars.

You have deep expertise in:
- Automotive lighting regulations (ECE, FMVSS, UNECE R112, R123, R148)
- LED technology: matrix, pixel, adaptive, sequential turn signals
- Automotive OEM purchasing processes, RFQ/RFI cycles, and SOP timelines
- Key global OEMs: Stellantis, Volkswagen Group, BMW Group, Mercedes-Benz, Renault-Nissan,
  Toyota, Hyundai-Kia, GM, Ford, Geely, BYD, SAIC
- Competitive landscape: Hella, Marelli, Koito, Stanley, ZKW, SL Corporation, Gentex

RESPONSE RULES — CRITICAL:
1. ALWAYS respond with a single valid JSON object. No markdown code fences, no prose outside JSON.
2. Use exactly this top-level structure every time:
{
  "agent": "Valeo Visibility OEM Analyst",
  "session_turn": <integer, incremented each reply>,
  "customer": {
    "oem_name": "<string or null>",
    "region": "<EMEA | APAC | NAFTA | Global | null>",
    "platform_program": "<string or null>"
  },
  "project": {
    "light_function": "<headlamp | rear_lamp | drl | fog | interior | combination | null>",
    "led_technology": "<matrix | pixel | adaptive | sequential | standard | null>",
    "vehicle_segment": "<A | B | C | D | E | F | SUV | LCV | null>",
    "sop_year": "<integer or null>"
  },
  "analysis": {
    "opportunity_score": <0-10 float or null>,
    "key_requirements": ["<string>"],
    "valeo_strengths": ["<string>"],
    "risks": ["<string>"],
    "competitive_threats": ["<string>"],
    "recommendation": "<string>"
  },
  "answer": "<direct answer to the user's question in plain text>",
  "follow_up_questions": ["<string>"]
}
3. Populate only fields for which you have information; set unknown fields to null or [].
4. Preserve and UPDATE customer/project context across the conversation — never reset it.
5. Increment session_turn by 1 on every reply.
""".strip()

# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
class ValeoOEMAnalystAgent:
    def __init__(self):
        self.client = Anthropic()
        self.conversation_history: list[dict] = []
        self.session_turn = 0

    def chat(self, user_message: str) -> dict:
        self.conversation_history.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=self.conversation_history,
        )

        raw_text = response.content[0].text.strip()

        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError:
            result = {"error": "Model returned non-JSON output", "raw": raw_text}

        self.conversation_history.append({"role": "assistant", "content": raw_text})
        self.session_turn += 1
        return result

    def run(self):
        print("\n=== Valeo Visibility OEM Customer Analysis Agent ===")
        print("Type 'quit' to exit.\n")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("Session ended.")
                break
            if not user_input:
                continue

            response_json = self.chat(user_input)
            print("\nAgent:", json.dumps(response_json, indent=2), "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = ValeoOEMAnalystAgent()
    agent.run()
