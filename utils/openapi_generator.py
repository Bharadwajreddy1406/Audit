import os
import sys

# Add the project root to the Python path (required for GitHub Actions)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from dotenv import load_dotenv
from utils.ast_parser import parse_flask_routes  # Ensure ast_parser is implemented and accessible

# Load environment variables
load_dotenv()

# Ensure the .env file is ignored by git
with open('.gitignore', 'a') as gitignore:
    gitignore.write('\n.env\n')

# Authenticate with the LLM service
api_key = os.getenv("TOKEN_4o")
if not api_key:
    raise ValueError("TOKEN_4o is not set in environment variables. Please set it in .env or GitHub Secrets.")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=api_key,
)

def generate_llm_description(route_metadata):
    """Send a request to the LLM to generate a route description."""
    prompt = f"""
    Generate API documentation for the following route:
    - Path: {route_metadata['path']}
    - Methods: {', '.join(route_metadata['methods'])}
    - Function Name: {route_metadata['function_name']}
    - Parameters: {', '.join(route_metadata['parameters'])}
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an API documentation assistant."},
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=1,
            max_tokens=512,
            top_p=1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating description with LLM: {e}")
        return "Description could not be generated."

def generate_openapi_spec_with_llm(routes):
    """Generate OpenAPI spec using the LLM for descriptions."""
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Flask API Documentation",
            "version": "1.0.0",
            "description": "Automated API documentation using LLM.",
        },
        "paths": {},
    }

    for route in routes:
        # Get LLM-generated description
        print(f"Processing route: {route['path']}")
        llm_description = generate_llm_description(route)
        
        # Populate OpenAPI spec
        openapi_spec["paths"][route["path"]] = {
            method.lower(): {
                "summary": llm_description,
                "parameters": [
                    {"name": param, "in": "query", "required": False, "schema": {"type": "string"}}
                    for param in route["parameters"]
                ],
                "responses": {
                    "200": {"description": "Successful response"},
                    "400": {"description": "Bad request"},
                },
            } for method in route["methods"]
        }

    return openapi_spec

if __name__ == "__main__":
    print("Parsing Flask routes...")
    routes = parse_flask_routes("app.py")
    print(f"Found {len(routes)} routes. Generating OpenAPI specification...")
    
    openapi_spec = generate_openapi_spec_with_llm(routes)
    
    # Save the OpenAPI spec to a file
    with open("openapi.json", "w") as f:
        json.dump(openapi_spec, f, indent=2)
    
    print("OpenAPI spec generated and saved to openapi.json")
