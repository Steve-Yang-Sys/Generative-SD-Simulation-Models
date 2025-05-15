from openai import OpenAI
from google import genai
from google.genai.types import GenerateContentConfig
import PIL.Image
import base64
import json
import re
from datetime import datetime
import xml.etree.ElementTree as ET


# Set your OpenAI API key (ensure this is kept secure)
openai_api_key = "YOUR_API_KEY"
# Set your Gemini API key (ensure this is kept secure)
GEMINI_API_KEY = "YOUR_API_KEY"

# set up the model configuration to reduce the unnecessary randomness produced each time.
gemini_config = GenerateContentConfig(
temperature=0.2,
top_p=0.95,
top_k=20,
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def extract_components_from_image(image_path, choice_of_LLM):
    """
    Extracts the components of a stock and flow diagram using the OpenAI/Gemini API.
    The function reads an image file, encodes it in base64, and sends it to the API
    with a prompt to extract stocks, flows, auxiliaries, and connectors.
    Each variable may now also include location keys "x" and "y".
    Expected output is a JSON object with keys: 'stocks', 'flows', 'auxiliaries', 'connectors'.
    """
    # Construct the prompt
    prompt = (
        "Analyze the following image of a stock and flow diagram in System Dynamics. "
        "Extract the following information in JSON format: stocks, flows, auxiliaries, and connectors. "
        "Return a JSON object with keys: 'stocks', 'flows', 'auxiliaries', 'connectors'. "
        "Each of 'stocks', 'flows', and 'auxiliaries' should be an array of objects with a 'name' property, a 'description' property for adding documentation and explanation for each variable suggested by you, a 'unit' property for reasonable units that you suggest, and an 'eqn' property for sound equations that you suggest. (Note: you should suggest numbers instead of formulas in 'string' type for all the stocks)"
        "As well as their relative location information in the given image: 'x' and 'y' coordinates (in pixels). "
        "For stocks, also extract 'inflows' and 'outflows' as lists of flow names. "
        "List all the names as original. "
        "Each connector should be an object with properties 'src' and 'tgt' and ONLY take the arrow links between model variables into account. "
        "You need to add the causal links from 'stock' to 'flow' in the 'connectors' part if the variable name of 'stock' is used in the suggested 'flow' equation. "
        "To avoid any omissions, make sure and check every object with properties 'src' and 'tgt' in 'connectors' has been classified as either 'stocks', or 'flows', or 'auxiliaries'. "
        "Add their causal relationships in 'connectors' part if any variable is used as part of the equation of another variable. "
    )
    # Construct the LLM: OpeanAI or Gemini?
    if choice_of_LLM == "OpenAI".upper():
        # Extract the components using the OpenAI API
        # Read and encode the image file
        base64_image = encode_image(image_path)
        client = OpenAI(api_key=openai_api_key)

        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ],
            text={"format": {"type": "json_object"}},
            temperature=1,
            top_p=0.1
        )

        # Debug: Print the entire API response to see its structure
        print("Raw API response:")
        print(response)

        # Extract and check the response content
        structured_data = response.output_text
        # with open("structured_data_OpenAI.txt", "w", encoding="utf-8") as text_file:
        #     text_file.write(structured_data)
        if not structured_data.strip():
            raise ValueError("API returned an empty response. Check your model access, prompt, and image input.")
    else:
        image = PIL.Image.open(image_path)
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image],
            config=gemini_config
        )

        # Debug: Print the entire API response to see its structure
        print("Raw API response:")
        print(response)

        # Extract and check the response content
        structured_data = response.candidates[0].content.parts[0].text
        # Step 1: Clean up raw response
        structured_data = re.sub(r"```(?:json)?", "", structured_data).strip()
        # Step 2: Extract JSON portion
        json_match = re.search(r'\{.*\}', structured_data, re.DOTALL)
        if json_match:
            structured_data = json_match.group()
            # with open("structured_data_Gemini.txt", "w", encoding="utf-8") as text_file:
            #     text_file.write(structured_data)
        else:
            raise ValueError("No valid JSON found in API response")

    # Parse the JSON from the API response
    try:
        model_data = json.loads(structured_data)
        with open('output.json', 'w') as outfile:
            json.dump(model_data, outfile, indent=2)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON. The extracted content is:")
        print(structured_data)
        raise e

    return model_data

def extract_variable_names(model_data):
    names = []
    for category in ["stocks", "flows", "auxiliaries"]:
        for item in model_data.get(category, []):
            names.append(item["name"])
    return names

def clean_eqn(eqn, variable_names):
    """
    Replace spaces in known variable names with underscores in the given equation.
    """
    # Sort by length (longest names first to avoid partial replacements)
    variable_names = sorted(variable_names, key=len, reverse=True)

    for name in variable_names:
        underscored = name.replace(" ", "_")
        pattern = r'\b' + re.escape(name) + r'\b'
        eqn = re.sub(pattern, underscored, eqn)

    return eqn

def generate_xmile(model_data, filename):
    """
    Converts the structured model data into an XMILE file.
    """
    # Create the root XMILE element
    xmile = ET.Element("xmile", {"version": "1.0"})

    # Add header information
    header = ET.SubElement(xmile, "header")
    model_name = ET.SubElement(header, "name")
    model_name.text = "Converted System Dynamics Model"

    # Simulation specifications - subject to user change
    sim_specs = ET.SubElement(xmile, "sim_specs")
    start = ET.SubElement(sim_specs, "start")
    start.text = "0"
    stop = ET.SubElement(sim_specs, "stop")
    stop.text = "100"
    dt = ET.SubElement(sim_specs, "dt")
    dt.text = "1/4"

    # Model section
    model = ET.SubElement(xmile, "model")
    variables = ET.SubElement(model, "variables")
    names = extract_variable_names(model_data)

    # Add stocks
    for stock in model_data.get("stocks", []):
        stock_el = ET.SubElement(variables, "stock", {"name": stock["name"]})

        if "description" in stock and stock["description"]:
            doc_el = ET.SubElement(stock_el, "doc")
            doc_el.text = stock["description"]

        if "eqn" in stock and stock["eqn"]:
            eqn_el = ET.SubElement(stock_el, "eqn")
            eqn_el.text = stock["eqn"]

        # Add inflow tags if available
        for inflow in stock.get("inflows", []):
            ET.SubElement(stock_el, "inflow").text = inflow.replace(" ", "_")
        for outflow in stock.get("outflows", []):
            ET.SubElement(stock_el, "outflow").text = outflow.replace(" ", "_")

        if "unit" in stock and stock["unit"]:
            doc_el = ET.SubElement(stock_el, "units")
            doc_el.text = stock["unit"]

    # Add flows
    for flow in model_data.get("flows", []):
        flow_el = ET.SubElement(variables, "flow", {"name": flow["name"]})

        if "description" in flow and flow["description"]:
            doc_el = ET.SubElement(flow_el, "doc")
            doc_el.text = flow["description"]

        if "eqn" in flow and flow["eqn"]:
            eqn_el = ET.SubElement(flow_el, "eqn")
            eqn_el.text = clean_eqn(flow["eqn"], names)

        if "unit" in flow and flow["unit"]:
            doc_el = ET.SubElement(flow_el, "units")
            doc_el.text = flow["unit"]

    # Add auxiliary variables
    for aux in model_data.get("auxiliaries", []):
        aux_el = ET.SubElement(variables, "aux", {"name": aux["name"]})

        if "description" in aux and aux["description"]:
            doc_el = ET.SubElement(aux_el, "doc")
            doc_el.text = aux["description"]

        if "eqn" in aux and aux["eqn"]:
            eqn_el = ET.SubElement(aux_el, "eqn")
            eqn_el.text = clean_eqn(aux["eqn"], names)

        if "unit" in aux and aux["unit"]:
            doc_el = ET.SubElement(aux_el, "units")
            doc_el.text = aux["unit"]

    # Create views element and a single view element
    views = ET.SubElement(model, "views")
    view = ET.SubElement(views, "view")

    # Grid layout settings
    grid_spacing_x = 300
    grid_spacing_y = 200
    stock_start_x = 400
    stock_start_y = 400

    # Position trackers
    stock_positions = {}
    flow_positions = {}
    aux_positions = {}
    var_positions = {}

    # Add connector elements in the view with sequential uid starting from 1
    connectors = model_data.get("connectors", [])
    for i, conn in enumerate(connectors, start=1):
        connector_attribs = {
            "uid": str(i),  # Sequential uid starting from 1
            "angle": str(conn.get("angle", "0"))
        }
        connector_el = ET.SubElement(view, "connector", attrib=connector_attribs)
        from_el = ET.SubElement(connector_el, "from")
        from_el.text = conn["src"]
        to_el = ET.SubElement(connector_el, "to")
        to_el.text = conn["tgt"]

    # Output display objects for variables
    for i, stock in enumerate(model_data.get("stocks", [])):
        x = stock_start_x + (i % 4) * grid_spacing_x
        y = stock_start_y + (i // 4) * grid_spacing_y
        stock_positions[stock["name"]] = (x, y)
        var_positions[stock["name"]] = (x, y)
        attribs = {
            "x": str(stock.get("x", str(x))),
            "y": str(stock.get("y", str(y))),
            "name": stock["name"]
        }
        ET.SubElement(view, "stock", attrib=attribs)

    for i, flow in enumerate(model_data.get("flows", [])):
        name = flow["name"]

        # Try to find connected stocks
        from_stock = next((s["name"] for s in model_data["stocks"] if name in s.get("outflows", [])), None)
        to_stock = next((s["name"] for s in model_data["stocks"] if name in s.get("inflows", [])), None)

        if from_stock and to_stock:
            x1, y1 = stock_positions[from_stock]
            x2, y2 = stock_positions[to_stock]
            x = (x1 + x2) // 2
            y = (y1 + y2) // 2
        elif to_stock:
            x, y = stock_positions[to_stock]
            x -= 100
        elif from_stock:
            x, y = stock_positions[from_stock]
            x += 100
        else:
            x = 100 + (i * 150)
            y = 500

        flow_positions[name] = (x, y)
        var_positions[name] = (x, y)

        attribs = {
            "x": str(flow.get("x", str(x))),
            "y": str(flow.get("y", str(y))),
            "name": flow["name"]
        }
        # ET.SubElement(view, "flow", attrib=attribs)
        flow_view = ET.SubElement(view, "flow", attrib=attribs)
        # Generate <pts> in view as well using the same rule:
        try:
            flow_x = float(flow.get("x", str(x)))
        except ValueError:
            flow_x = 0.0
        flow_y = flow.get("y", str(y))
        pts_el = ET.SubElement(flow_view, "pts")
        ET.SubElement(pts_el, "pt", attrib={"x": str(flow_x - 60), "y": str(flow_y)})
        ET.SubElement(pts_el, "pt", attrib={"x": str(flow_x + 60), "y": str(flow_y)})

    aux_indices = {}
    for i, aux in enumerate(model_data.get("auxiliaries", [])):
        name = aux["name"]

        # Find what this auxiliary connects to
        target = next((c["tgt"] for c in model_data.get("connectors", []) if c["src"] == name), None)
        base_x, base_y = var_positions.get(target, (100 + (i * 200), 700))

        # Offset for visual clarity
        offset = aux_indices.get(target, 0)
        x = base_x
        y = base_y - 100 - (offset * 30)
        aux_indices[target] = offset + 1

        aux_positions[name] = (x, y)
        var_positions[name] = (x, y)

        attribs = {
            "x": str(aux.get("x", str(x))),
            "y": str(aux.get("y", str(y))),
            "name": aux["name"]
        }
        ET.SubElement(view, "aux", attrib=attribs)

    # Write the XMILE file
    tree = ET.ElementTree(xmile)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def print_summary(model_data):
    """
    Prints a summary of the model data, including the number of stocks, flows,
    and auxiliary variables, as well as their names.
    """
    stocks = model_data.get("stocks", [])
    flows = model_data.get("flows", [])
    auxiliaries = model_data.get("auxiliaries", [])
    connectors = model_data.get("connectors", [])

    print("\nModel Summary:")
    print(f"Number of stocks: {len(stocks)}")
    print("Stocks:", ", ".join([stock["name"] for stock in stocks]))

    print(f"\nNumber of flows: {len(flows)}")
    print("Flows:", ", ".join([flow["name"] for flow in flows]))

    print(f"\nNumber of auxiliary variables: {len(auxiliaries)}")
    print("Auxiliaries:", ", ".join([aux["name"] for aux in auxiliaries]))

    print(f"\nNumber of connectors: {len(connectors)}")

def main():
    # Replace with the path to your stock and flow diagram image file.
    image_path = "YOUR_LOCAL_IMAGE_PATH"
    # Step 1: Choose the LLM API
    choice_of_LLM = input("OpenAI or Gemini?").upper().strip()
    model_data = extract_components_from_image(image_path, choice_of_LLM)

    print("Extracted model data:")
    print(json.dumps(model_data, indent=2))

    # Print summary of the extracted model data
    print_summary(model_data)

    # Step 2: Generate the XMILE file from the extracted model data
    timestamp = datetime.now().strftime("%m-%d")
    xmile_filename = f"SD_Model_{choice_of_LLM}_{timestamp}.xmile"
    generate_xmile(model_data, xmile_filename)
    print(f"XMILE file '{xmile_filename}' generated successfully!")


if __name__ == "__main__":
    main()
