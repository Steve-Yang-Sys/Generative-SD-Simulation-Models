# User Guide
This repository contains Python codes to transform textual outputs from Large Language Models (LLMs) like ChatGPT and Gemini into standard XMILE model files that can be directly open on most System Dynamics (SD) software tools. It encompasses two parts: 1. **JSON-to-XMILE Converter (no API required)**; 2. **SD Model Image Identification with API**. In the first case, users can talk with LLMs on the website and ask them to export model information directly in JSON data format. Regarding the second application, programmers or developers can directly send prompts within the API call for SD model image identification. Users are free to choose the way depending on their own preference.

---

# 🧭 JSON-to-XMILE Converter (no API required)

This tool allows you to convert structured **JSON model outputs** (from tools like ChatGPT or Gemini) into an **XMILE model file** that you can open in SD software like **Stella**, **Vensim**, or **Insight Maker**.

## 🧠 How It Works (Simplified)

The script reads your model structure from model.json
1. It cleans variable names (replaces spaces with underscores)
2. It creates XML tags following the XMILE format
3. It writes the result to "Exported_SD_Model.xmile", ready for simulation

## ✅ Requirements

- Python 3 installed
- A valid JSON model file (`model.json`)
- The Python script: `JSON_to_XMILE.py`


## 📁 Step 1: File Preparation

1. Create and export a JSON model output from your LLM (e.g., ChatGPT or Gemini) by using the suggested prompts.
 ```
    As a system dynamics expert, I hope you can suggest a system dynamics model on "**DESCRIBE YOUR QUESTION HERE**", and strictly follow all the texts in the prompt as given below: 
prompt = (
        "Use plain texts for all the variable names and extract the following information in JSON format: stocks, flows, auxiliaries, and connectors. "
        "Return a JSON object with keys: 'stocks', 'flows', 'auxiliaries', 'connectors'. "
        "Each of 'stocks', 'flows', and 'auxiliaries' should be an array of objects with a 'name' property, a 'description' property for adding documentation and explanation for each variable suggested by you, a 'unit' property for reasonable units that you suggest, and an 'eqn' property for reasonable equations that you may suggest. Note: you should only suggest initial values for all the equations of 'stocks'. "
        "For stocks, also extract 'inflows' and 'outflows' as lists of flow names. "
        "Each connector should be an object with properties 'src' and 'tgt' and they are different from flows. If there is a causal link from 'stock' to 'flow' or other 'auxiliaries', their relationships should be considered in the 'connectors' part. " 
)
 ```
3. Save that content into a file named: "model.json". 💡 You can copy-paste the JSON text into a file using any text editor (e.g., Notepad, VS Code) and save it as model.json.
4. Place this file in the same folder as the Python script of "JSON_to_XMILE.py".


## 🧾 Step 2: Understand the Required JSON Format

Make sure your "model.json" follows this structure:

```json
{
"stocks": [
 {
   "name": "Population",
   "equation": "Births - Deaths",
   "doc": "Total population in the system."
 }
],
"flows": [
 {
   "name": "Births",
   "equation": "Birth_Rate * Population",
   "doc": "New births per time unit."
 }
],
"auxiliaries": [
 {
   "name": "Birth Rate",
   "equation": "0.02",
   "doc": "Fixed birth rate."
 }
]
}
```

## ▶️ Step 3: Run the Python Script

1. Run the Python script of "JSON_to_XMILE.py" in any IDEs like PyCharm, Jupyter Notebooks, or others.
2. If everything works, a new file called "Exported_SD_Model.xmile" will be created in the same folder.


## 📂 Step 4: Open the XMILE File

You can now open output.xmile in any software that supports the XMILE standard, such as: Stella Architect/Professional, Insight Maker (free online tool), Vensim.


## 💡 Tips & Troubleshooting

| Problem                         | Solution                                                       |
| ------------------------------- | -------------------------------------------------------------- |
| `ModuleNotFoundError`           | Make sure Python is properly installed                         |
| `FileNotFoundError: model.json` | Ensure `model.json` is in the same folder as the Python script |
| Equations look wrong            | Make sure variable names match exactly (case sensitive)        |

---

# SD Model Image Identification with API

This Python script leverages Large Language Models (OpenAI's GPT-4o or Google's Gemini) to analyze an image of a stock and flow diagram (SFD). It extracts components like stocks, flows, auxiliaries, and connectors, and then converts this information into an XMILE (XML Interchange Language for System Dynamics) file. This XMILE file can then be used with various SD modeling software.

## Description

The primary goal of this script is to automate the process of transcribing a visual SFD into a stanadard XMILE model file. It uses multimodal LLMs to interpret the diagram from an image file, identify its components, and suggest equations, units, and descriptions for each.

## Features

* **Image-based Model Extraction**: Analyzes an image (e.g., JPG, PNG) of a stock and flow diagram.
* **LLM Integration**: Supports both OpenAI (GPT-4o) and Google Gemini models for component extraction.
* **Component Identification**: Extracts stocks (with inflows/outflows), flows, auxiliary variables, and connectors.
* **Data Enrichment**: The LLM suggests:
    * Descriptions/documentation for each variable.
    * Reasonable units for variables.
    * Sound equations for flows and auxiliaries (stocks are initialized with numerical values).
    * Relative 'x' and 'y' coordinates for diagram elements.
* **JSON Output**: Saves the extracted model data in a structured JSON file (`output.json`).
* **XMILE Generation**: Converts the extracted data into a valid XMILE file.
* **View Information**: Attempts to replicate the visual layout in the XMILE file's view section based on extracted or inferred coordinates.
* **Summarization**: Prints a summary of the extracted components.

## Requirements

* Python 3
* `openai` library: `pip install openai`
* `google-generativeai` library: `pip install google-generativeai`
* `Pillow` (PIL) library: `pip install Pillow`

You will also need API keys for the chosen LLM:
* OpenAI API Key
* Google Gemini API Key

## Setup

1.  **Clone the repository or download the script.**
2.  **Install the required Python libraries**:
    ```bash
    pip install openai google-generativeai Pillow
    ```
3.  **Set API Keys**:
    Open the script (`SD Model Image Identification (API).py`) and replace the placeholder API keys with your actual keys:
    ```python
    openai_api_key = "YOUR_OPENAI_API_KEY"  # Replace with your OpenAI API key
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"    # Replace with your Google Gemini API key
    ```
    **Important**: Keep your API keys secure and do not commit them to public repositories. Consider using environment variables or a configuration file for managing API keys in a production environment.
4.  **Prepare your Image**:
    Have an image file (e.g., `.jpg`, `.png`) of the SFD you want to process.

## Usage

1.  **Run the script from your terminal**:
    ```bash
    python "SD Model Image Identification (API).py"
    ```
2.  **Update Image Path**:
    Modify the `image_path` variable in the `main()` function within the script to point to your SFD image file:
    ```python
    def main():
        image_path = "YOUR_LOCAL_IMAGE_PATH"  # <<< CHANGE THIS
        # ... rest of the main function
    ```
3.  **Choose LLM**:
    When prompted, enter whether you want to use "OpenAI" or "Gemini" for the analysis:
    ```
    OpenAI or Gemini?
    ```
    Type your choice and press Enter.
4.  **Output**:
    * The script will print the raw API response from the LLM.
    * It will then print the extracted model data in JSON format.
    * A summary of the extracted components (number of stocks, flows, auxiliaries, connectors, and their names) will be displayed.
    * An XMILE file named `SD_Model_[OpenAI/Gemini]_[MM-DD].xmile` (e.g., `SD_Model_OpenAI_05-15.xmile`) will be generated in the same directory as the script.
    * A JSON file named `output.json` containing the structured data extracted by the LLM will also be created.

## How it Works

1.  **Image Encoding**: The input image is encoded into base64 format to be sent to the LLM API.
2.  **LLM Prompting**: A detailed prompt is constructed, instructing the LLM to analyze the stock and flow diagram and extract stocks, flows, auxiliaries, connectors, their names, descriptions, units, equations, and relative x/y coordinates in a JSON format.
3.  **API Interaction**:
    * **OpenAI**: Uses the `gpt-4o` model with JSON mode enabled. Users are free to choose their preferred model version.
    * **Gemini**: Uses the `gemini-2.0-flash` model.
4.  **JSON Parsing**: The LLM's response (expected to be JSON) is parsed into a Python dictionary.
5.  **XMILE Generation (`generate_xmile` function)**:
    * An XML structure conforming to the XMILE standard is built using `xml.etree.ElementTree`.
    * **Header**: Basic model name and simulation specifications (start time, stop time, dt) are added. These are default values and can be modified in the script or the XMILE file later.
    * **Variables**: Stocks, flows, and auxiliary variables are created in the `<variables>` section.
        * Equations (`<eqn>`), documentation (`<doc>`), and units (`<units>`) are added if provided by the LLM.
        * For stocks, inflows (`<inflow>`) and outflows (`<outflow>`) are listed.
        * Variable names in equations are "cleaned" by the `clean_eqn` function, replacing spaces with underscores to ensure XMILE compatibility.
    * **Views**: A `<view>` section is created to represent the diagram visually.
        * Connectors (`<connector>`) are added with `uid`, `angle`, `from` (source), and `to` (target) elements.
        * Stocks, flows, and auxiliaries are placed in the view with `x` and `y` coordinates. The script attempts to use the coordinates provided by the LLM. If not available, it calculates positions based on a grid layout or relationships between elements (e.g., placing flows between their connected stocks).
6.  **File Output**: The generated XMILE structure is written to a `.xmile` file. The extracted JSON data is saved to `output.json`.

## Output Files

* **`SD_Model_[OpenAI/Gemini]_[MM-DD].xmile`**: The generated XMILE file that can be imported into SD modelling software (e.g., Vensim, Stella, Insight Maker).
* **`output.json`**: A JSON file containing the structured data extracted by the LLM from the image. This can be useful for debugging or further processing.

## Limitations and Considerations

* **API Costs**: Using OpenAI or Gemini APIs incurs costs based on usage. Be mindful of the pricing models for these services.
* **LLM Accuracy**: The accuracy of the extracted components, equations, and especially coordinates depends heavily on the quality of the input image and the capabilities of the chosen LLM. Complex or poorly drawn diagrams may result in errors or omissions.
* **Coordinate Accuracy**: While the script attempts to use or infer 'x' and 'y' coordinates, the visual layout in the generated XMILE file might require manual adjustment in the SD software.
* **Equation Validity**: The LLM suggests equations. These should always be reviewed for correctness and appropriateness to the model's logic.
* **Error Handling**: The script includes some basic error handling, particularly for JSON parsing and API responses. However, more robust error handling might be needed for production use.
* **Prompt Engineering**: The quality of the output is highly dependent on the prompt sent to the LLM. The current prompt is designed for typical stock and flow diagrams but might need adjustments for specific or unconventional diagram styles.
* **Model Configuration**: The Gemini model configuration (`gemini_config`) is set for lower temperature (0.2) to reduce randomness. OpenAI's call specifies a temperature of 1 and top_p of 0.1. These parameters can be tweaked to potentially improve results. There may be necessary adjustments on API call functions if the syntax for APIs changes with the new versions of LLMs.

## Future Improvements

* More sophisticated layout algorithms for the XMILE view.
* Allowing users to fine-tune LLM parameters.
* Support for more XMILE features (e.g., graphical functions, submodels).
* Interactive validation or correction of the extracted data before XMILE generation.
* Direct integration with SD software APIs if available.

## Contributing

Contributions are welcome! If you have suggestions for improvements or find any issues, please feel free to contact me.

---

## 👩‍💻 Author

Created by Zhenghua (Steve) Yang, with the love ❤️ and help 🙏 from AI chatbots.
Feel free to customize or extend it!
