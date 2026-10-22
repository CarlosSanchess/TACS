import requests

# BESSER Web Editor API endpoint
url = "https://editor.besser-pearl.org/besser_api/get-svg"

# Send the B-UML Python file to the web API
with open("models.py", "rb") as file_handle:
    files = {"buml_file": ("models.py", file_handle, "text/x-python")}
    response = requests.post(url, files=files)

if response.status_code == 200:
    with open("problem_dsl_diagram.svg", "wb") as output_file:
        output_file.write(response.content)
    print("Success: Diagram saved as 'problem_dsl_diagram.svg'")
else:
    print(f"Error {response.status_code}: {response.text}")