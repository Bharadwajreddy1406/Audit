import json
from utils.ast_parser import parse_flask_routes

def generate_openapi_spec(routes):
    """Generate OpenAPI specification from parsed routes."""
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Flask API Documentation",
            "version": "1.0.0",
            "description": "Automated API documentation for Flask app."
        },
        "paths": {}
    }
    for route in routes:
        openapi_spec["paths"][route["path"]] = {
            method.lower(): {
                "summary": f"Handler function: {route['function']}",
                "parameters": [
                    {"name": param, "in": "query", "required": False, "schema": {"type": "string"}}
                    for param in route["parameters"]
                ],
                "responses": {
                    "200": {"description": "Successful response"},
                    "400": {"description": "Bad request"},
                }
            } for method in route["methods"]
        }
    return openapi_spec

def save_openapi_spec(spec, file_path):
    """Save OpenAPI spec to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(spec, file, indent=2)

if __name__ == "__main__":
    routes = parse_flask_routes("app.py")
    openapi_spec = generate_openapi_spec(routes)
    save_openapi_spec(openapi_spec, "openapi.json")
    print("OpenAPI spec generated and saved as openapi.json")
