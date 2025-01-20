from langchain.llms import OpenAI
from langchain.agents import initialize_agent, Tool
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set environment variables
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
os.environ["SERPAPI_API_KEY"] = "your_serpapi_api_key"

# Define utility functions
def fetch_form_fields_with_edge(url):
    try:
        edge_options = Options()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")

        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)

        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        inputs = driver.find_elements(By.TAG_NAME, "input")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        selects = driver.find_elements(By.TAG_NAME, "select")

        fields = []

        for input_field in inputs:
            field_info = {
                "tag": "input",
                "name": input_field.get_attribute("name"),
                "type": input_field.get_attribute("type"),
                "placeholder": input_field.get_attribute("placeholder"),
                "value": input_field.get_attribute("value"),
            }
            fields.append(field_info)

        for textarea in textareas:
            field_info = {
                "tag": "textarea",
                "name": textarea.get_attribute("name"),
                "placeholder": textarea.get_attribute("placeholder"),
            }
            fields.append(field_info)

        for select in selects:
            options = [
                option.text for option in select.find_elements(By.TAG_NAME, "option")
            ]
            field_info = {
                "tag": "select",
                "name": select.get_attribute("name"),
                "options": options,
            }
            fields.append(field_info)

        driver.quit()

        if not fields:
            return "No input fields, textareas, or selects were found on the page."

        return fields

    except Exception as e:
        return f"Error occurred: {e}"

def edge_form_tool(url: str):
    """Custom tool to extract form-like fields from a webpage using Edge (headless)."""
    form_data = fetch_form_fields_with_edge(url)
    return form_data


# Initialize the LLM
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0, max_tokens=512)

# Wrap the custom function as a Tool
tools = [
    Tool(
        name="EdgeFormTool",
        func=lambda url: edge_form_tool(url),  # Pass the URL to the function
        description="Fetch and extract form fields (input, textarea, select) from any webpage using Microsoft Edge. Provide a query with a valid URL.",
    )
]

# Initialize the agent
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True,
)


# Define the Agent class
class Agent:
    def __init__(self):
        pass  # Simplified initialization

    def run(self, url: str):
        """Run the agent with a URL input."""
        return agent.run(url)
