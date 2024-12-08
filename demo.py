
# MeWayWise
# This is the implementation of the travel mode reccomendation that combines 
# local document processing and an LLM to provide users with travel suggestions based on indivual preferences. 
# The system uses a local dataset and processes user queries to return personalized recommendations.



# Standard library imports
import pandas as pd
import itertools
from fuzzywuzzy import process
import json
import shutil
import sys
import threading
import time
import urllib.parse
import urllib.request

# Third-party imports
from openai import OpenAI

# Initialize LM Studio client
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
# MODEL = "llama-3.2-3b-qnn"
MODEL = "qwen2.5-coder-32b-instruct"

# read local document
# refer to local_doc.py to know more about the local document.
path = "C:\\Users\\qc_wo\\Desktop\\"
df = pd.read_csv(f"{path}travel_data.csv")
print("document opened. ")


# function design

def fuzzy_match(input_location, available_locations):
    """
    Matches a user-input location to the closest option in the dataset using fuzzy matching.
    """
    match, score = process.extractOne(input_location, available_locations)
    if score > 70:  # Accept matches with a confidence score above the threshold
        return match
    else:
        return None

def fetch_recommended_mode(origin, destination, preferences):
    """
    Recommends the best travel mode based on user preferences.
    """
    try:
        # Fuzzy match origin and destination
        matched_origin = fuzzy_match(origin, list(df.origin.unique()))
        matched_destination = fuzzy_match(destination, list(df.destination.unique()))
        # print(matched_origin, matched_destination)

        if not matched_origin or not matched_destination:
            return {"status": "error", "message": "Origin or destination could not be matched."}

        # Filter dataset for the given OD pair
        filtered_data = df[(df["origin"] == matched_origin) & (df["destination"] == matched_destination)]
        # print(filtered_data)

        if filtered_data.empty:
            return {"status": "error", "message": "No data available for the selected OD pair."}

        # Sort data based on preferences
        if preferences.get("priority") == "lowest_cost":
            recommendation = filtered_data.nsmallest(1, "fare_cost")
        elif preferences.get("priority") == "minimal_walking":
            recommendation = filtered_data.nsmallest(1, "energy_cost")
        elif preferences.get("priority") == "least_environmental_cost":
            recommendation = filtered_data.nsmallest(1, "co2_cost")
        elif preferences.get("priority") == "shortest_time":
            recommendation = filtered_data.nsmallest(1, "time_cost")
        else:
            return {"status": "error", "message": "Unknown preference priority."}

        # Return the recommended mode
        mode = recommendation.iloc[0].to_dict()
        return {"status": "success", "mode": mode}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Define the tool for LM Studio to understand the travel mode priority 
TRAVEL_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_recommended_mode",
        "description": "Recommend the best travel mode for a given origin-destination pair based on user preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Starting location."},
                "destination": {"type": "string", "description": "Destination location."},
                "preferences": {
                    "type": "object",
                    "properties": {
                        "priority": {
                            "type": "string",
                            "description": "User's primary preference (e.g., 'lowest_cost', 'minimal_walking', 'shortest_time','least_environmental_cost')."
                        }
                    },
                    "required": ["priority"]
                },
            },
            "required": ["origin", "destination", "preferences"],
        },
    },
}

# Class for displaying the state of model processing 
# (copied from "tool use doc")
class Spinner:
    def __init__(self, message="Processing..."):
        self.spinner = itertools.cycle(["-", "/", "|", "\\"])
        self.busy = False
        self.delay = 0.1
        self.message = message
        self.thread = None

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def _spin(self):
        while self.busy:
            self.write(f"\r{self.message} {next(self.spinner)}")
            time.sleep(self.delay)
        self.write("\r\033[K")  # Clear the line

    def __enter__(self):
        self.busy = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.busy = False
        time.sleep(self.delay)
        if self.thread:
            self.thread.join()
        self.write("\r")  # Move cursor to beginning of line


def chat_with_llm():
    # System message with instructions
    system_message = {
        "role": "system",
        "content": (
            "You are a travel assistant that helps users plan their travel routes. "
            "Your role is to understand the user's query and return a structured JSON response with the following fields:"
            "- `origin` (string): The starting location specified by the user."
            "- `destination` (string): The target location specified by the user."
            "- `preferences` (object): An object with a single key, `priority`, which must have one of the following values:"
            "    - `lowest_cost`"
            "    - `minimal_walking`"
            "    - `shortest_time`"
            "    - `least_environmental_cost`"
            "### Requirements:"
            "1. Always respond in a SINGLE JSON format. Do not include explanations or narratives."
            "2. If unable to determine fields, set their values to `null`."
        ),
    }

    print(
        "Assistant: Hi! I can help you plan your travel routes based on your preferences. "
        "Let me know where you want to go and what matters most to you (e.g., minimal walking, less cost)."
    )
    print("(Type 'quit' to exit)")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break

        # Reset the messages list for each query
        messages = [system_message, {"role": "user", "content": user_input}]

        try:
            with Spinner("Thinking..."):
                # Call the LLM for a response
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                )
                # print(f"response is :{response.choices[0].message}")
                llm_content = response.choices[0].message.content

                # Parse the response
                try:
                    parsed_input = json.loads(llm_content)  
                except json.JSONDecodeError:
                    print("\nAssistant: I couldn't parse the response. Could you rephrase your query?")
                    continue

                # Validate the response structure
                origin = parsed_input.get("origin")
                destination = parsed_input.get("destination")
                preferences = parsed_input.get("preferences")

                if not origin or not destination or not preferences:
                    print("\nAssistant: I couldn't understand your request. Could you clarify?")
                    continue

                # Call the travel recommendation function
                result = fetch_recommended_mode(origin, destination, preferences)

                if result["status"] == "success":
                    mode = result["mode"]
                    print(
                        f"\nAssistant: The best travel mode from {origin} to {destination} is '{mode['mode']}'.\n"
                        f"Details:\n- Time: {mode['time_cost']} minutes\n"
                        f"- Cost: ${mode['fare_cost']}\n"
                        f"- Emissions: {mode['co2_cost']} kg CO2\n"
                        f"- Walking Distance: {mode['energy_cost']} meters"
                    )
                else:
                    print(f"\nAssistant: {result['message']}")

        except Exception as e:
            print(f"\nError: {str(e)}")


# implement the code
if __name__ == "__main__":
    chat_with_llm()
