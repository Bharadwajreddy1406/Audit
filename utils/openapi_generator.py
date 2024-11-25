import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from utils.ast_parser import parse_flask_routes

# Load environment variables
load_dotenv()

# Authenticate with OpenAI
api_key = os.getenv("TOKEN_4O")
if not api_key:
    raise ValueError("TOKEN_4O is not set in environment variables. Please set it in .env or GitHub Secrets.")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=api_key,
)

def generate_html_from_openapi(openapi_spec):
    """Generate HTML documentation from OpenAPI spec using LLM."""
    # Convert OpenAPI spec into a readable format
    openapi_spec_json = json.dumps(openapi_spec, indent=2)
    prompt = f"""
    Generate an HTML page for API documentation based on the following OpenAPI JSON:
    {openapi_spec_json}

    The HTML should include:
    - A title
    - A description of the API
    - Each endpoint listed with its path, method, parameters, and a brief description
    - A clean, user-friendly layout
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in generating HTML for API documentation."},
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating HTML with LLM: {e}")
        return "<html><body><h1>Error Generating Documentation</h1></body></html>"

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
        prompt = f"""
        Generate a summary for this API route:
        Path: {route['path']}
        Methods: {', '.join(route['methods'])}
        Parameters: {', '.join(route['parameters'])}
        """
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an API documentation assistant."},
                    {"role": "user", "content": prompt},
                ],
                model="gpt-4o",
                temperature=0.7,
                max_tokens=256,
                top_p=1,
            )
            description = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating description for {route['path']}: {e}")
            description = "No description available."

        openapi_spec["paths"][route["path"]] = {
            method.lower(): {
                "summary": description,
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
    
    print("Generating HTML documentation...")
    html_content = generate_html_from_openapi(openapi_spec)

    # Save the HTML to index.html
    with open("index.html", "w") as f:
        f.write(html_content)
    
    print("HTML documentation generated and saved to index.html")
