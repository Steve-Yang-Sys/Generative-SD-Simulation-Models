# Generative-SD-Simulation-Models
This repository contains Python code to transform textual outputs from Large Language Models (LLMs) like ChatGPT and Gemini into standard XMILE model file that can be directly open on most System Dynamics (SD) software tools. It encompasses two parts: 1. directly talk with LLMs on the website and export JSON data file manually; 2. use API call.

# 🧭 JSON-to-XMILE Converter

This tool allows you to convert structured **JSON model outputs** (from tools like ChatGPT or Gemini) into an **XMILE model file** that you can open in system dynamics software like **Stella**, **Vensim**, or **Insight Maker**.

## 🧠 How It Works (Simplified)

The script reads your model structure from model.json
1. It cleans variable names (replaces spaces with underscores)
2. It creates XML tags following the XMILE format
3. It writes the result to "Exported_SD_Model.xmile", ready for simulation

---

## ✅ Requirements

- Python 3.x installed
- A valid JSON model file (`model.json`)
- The Python script: `Json_to_XMILE_Cleaned.py`

---

## 📁 Step 1: File Preparation

1. Create and export a JSON model output from your LLM (e.g., ChatGPT or Gemini) by using the suggested prompts.
2. Save that content into a file named: "model.json". 💡 You can copy-paste the JSON text into a file using any text editor (e.g., Notepad, VS Code) and save it as model.json.
3. Place this file in the same folder as the Python script of "JSON_to_XMILE.py".

---

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
---

## ▶️ Step 3: Run the Python Script

1. Run the Python script of "JSON_to_XMILE.py" in any IDEs like PyCharm, Jupyter Notebooks, or others.
2. If everything works, a new file called "Exported_SD_Model.xmile" will be created in the same folder.

---

## 📂 Step 4: Open the XMILE File

You can now open output.xmile in any software that supports the XMILE standard, such as: Stella Architect/Professional, Insight Maker (free online tool), Vensim.

---

## 💡 Tips & Troubleshooting

| Problem                         | Solution                                                       |
| ------------------------------- | -------------------------------------------------------------- |
| `ModuleNotFoundError`           | Make sure Python is properly installed                         |
| `FileNotFoundError: model.json` | Ensure `model.json` is in the same folder as the Python script |
| Equations look wrong            | Make sure variable names match exactly (case sensitive)        |

---
## 👩‍💻 Author

Created by Zhenghua (Steve) Yang.
Feel free to customize or extend it!
