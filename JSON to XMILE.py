import json
import re
import xml.etree.ElementTree as ET

def extract_variable_names(model_data):
    """Extracts variable names from stocks, flows, and auxiliaries."""
    names = []
    for category in ["stocks", "flows", "auxiliaries"]:
        for item in model_data.get(category, []):
            names.append(item["name"])
    return names

def clean_eqn(eqn, variable_names):
    """
    Replace spaces in known variable names with underscores in the given equation.
    Ensures correct matching by sorting longer names first.
    """
    # Sort by length (longest names first to avoid partial replacements)
    variable_names = sorted(variable_names, key=len, reverse=True)

    for name in variable_names:
        underscored = name.replace(" ", "_")
        pattern = r'\b' + re.escape(name) + r'\b'
        eqn = re.sub(pattern, underscored, eqn)

    return eqn

def generate_xmile_from_json(model_data, filename):
    """
    Converts the structured model data into an XMILE file.
    Builds the required XML structure and writes it to the specified file.
    """
    # Create the root XMILE element
    xmile = ET.Element("xmile", {"version": "1.0"})

    # Add header information
    header = ET.SubElement(xmile, "header")
    model_name = ET.SubElement(header, "name")
    model_name.text = "Converted System Dynamics Model"

    # Simulation specifications - subject to change by users
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

        # Add corresponding flow tags if available
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

    # Add connector elements in the view with sequential "uid" starting from 1
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
    # Replace "YOUR_LOCAL_JSON_FILE_PATH" with the path to your sample JSON file.
    json_filename = "YOUR_LOCAL_JSON_FILE_PATH"
    with open(json_filename, "r") as f:
        model_data = json.load(f)

    # Print summary of the extracted model data
    print_summary(model_data)

    # Set the filename to save - subject to change by users
    xmile_filename = "Exported_SD_Model.xmile"
    generate_xmile_from_json(model_data, xmile_filename)
    print(f"XMILE file '{xmile_filename}' generated successfully!")

if __name__ == "__main__":
    main()
