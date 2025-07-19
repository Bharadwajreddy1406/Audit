import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from ASTparser import parse_flask_routes

load_dotenv()

# Authenticate with OpenAI
token = os.getenv("TOKEN_GIT")
endpoint = "https://models.inference.ai.azure.com"

client = OpenAI(
    api_key=token,
    base_url=endpoint,
)

def generate_html_from_openapi(openapi_spec):
    """Generate HTML documentation from OpenAPI spec using LLM."""
    print("Generating HTML from OpenAPI spec...")
    # Convert OpenAPI spec into a readable format
    openapi_spec_json = json.dumps(openapi_spec, indent=2)
    
    # Example HTML for one route
    example_route_html = """
    <div class="endpoint">
        <h3>/example</h3>
        <p><span class="method">GET</span> - Example description for the route.</p>
        <h4>Parameters</h4>
        <p>No parameters required.</p>
        <h4>Responses</h4>
        <ul>
            <li><code>200</code>: Successful response</li>
            <li><code>400</code>: Bad request</li>
        </ul>
    </div>
    """
    
    prompt = f"""
    Generate an HTML page for API documentation based on the following OpenAPI JSON:
    {openapi_spec_json}

    The HTML should include:
    - A title
    - A description of the API only if doc Strings are provided
    - Each endpoint listed with its path, method, parameters, and a brief description
    - A clean, user-friendly layout

    Use the following exact HTML as a template for each route:
    {example_route_html}
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in generating HTML for API documentation."},
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=4096,  # Increase max_tokens to allow for a larger response
            top_p=1,
        )
        print("HTML generation successful.")
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating HTML with LLM: {e}")
        return "<html><body><h1>Error Generating Documentation</h1></body></html>"

def generate_openapi_spec_with_llm(routes):
    """Generate OpenAPI spec using the LLM for descriptions."""
    print("Generating OpenAPI spec with LLM...")
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
        print(f"Processing route: {route['path']}")
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
            print(f"Generated description for {route['path']}: {description}")
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

def display_html_content(file_path):
    """Read and print the content of the HTML file."""
    print(f"Displaying content of {file_path}...")
    try:
        with open(file_path, "r") as file:
            content = file.read()
            print(content)
    except Exception as e:
        print(f"Error reading HTML file: {e}")

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
    
    # Display the content of the generated HTML file
    display_html_content("index.html")
    
    print("OpenAPI Specification:")
    print(json.dumps(openapi_spec, indent=2))
