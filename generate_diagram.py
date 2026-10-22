import requests

def fetch_diagram(input_file: str, output_svg: str):
    url = "https://editor.besser-pearl.org/besser_api/get-svg"
    with open(input_file, "rb") as file_handle:
        files = {"buml_file": (input_file, file_handle, "text/x-python")}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        with open(output_svg, "wb") as output_file:
            output_file.write(response.content)
        print(f"Success: Diagram saved as '{output_svg}'")
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    fetch_diagram("models.py", "problem_dsl_diagram.svg")
    fetch_diagram("models_solution.py", "solution_dsl_diagram.svg")
