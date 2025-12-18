# Ollama‑Powered LLM CLI Toolkit
A lightweight command‑line interface for interacting with locally‑hosted Ollama models.
It provides convenient utilities for model management (listing, selecting, downloading) and two chat modes – a single‑shot response and a streaming “yield‑as‑you‑go” mode – all rendered with beautiful Rich output.
## Features
- **Model Management**
    - List locally available Ollama models.
    - Select a model interactively or by index.
    - Download new models with a progress bar that shows percentage, speed, ETA, and transferred data.
- **Chat Interfaces**
    - **Full‑response mode** – chat() streams the model’s answer, renders it live with Rich markdown, and returns the complete string
    - **Streaming mode** – chat_yield() yields each chunk as soon as it arrives, letting callers process partial output in real time while still displaying a live Rich view.
- **Rich UI**
    - Colorful console rules, tables, panels, and live markdown rendering for a pleasant developer experience.
- **Error Handling**
    - Unified handling of Ollama connection errors with clear, colored messages and graceful termination.
# Screenshots
![LLM CLI Toolkit-gif](./screenshots/Screen_Recording.gif)

## Requirements

To run this application, you'll need to install the following Python packages:

 * Python ≥ 3.8
 * Ollama installed and running locally (ollama serve).

### Setup
Step 1: **Clone the Repository**

```bash
git clone https://github.com/Mangaleshwaran2002/Ollama-Powered-LLM-CLI-Toolkit.git
cd ollama-cli-toolkit
```
Step 2: **Install dependencies**

```bash
pip install -r requirements.txt 
(or)
uv pip install -r requirements.txt 
```
Step 3: **Ensure Ollama is running**
```bash
ollama serve   # in a separate terminal
```
Step 4: **Run the demo script**
```bash
python app.py
(or)
uv run app.py
```

The script will prompt you to select a model (or download a new one) and then let you chat interactively.

## Contributing
Contributions are welcome! Follow these steps:

1. Fork the repo and create a feature branch.
2. Write tests (if adding new logic) and ensure existing ones pass.
3. Keep the code style consistent with black / flake8.
4. Submit a Pull Request with a clear description of the change.
5. Please open an issue first if you’re planning a large modification.

<<<<<<< HEAD
# License
This project is licensed under the MIT License - see the LICENSE file for details.
=======
## License
This project is licensed under the MIT License - see the LICENSE file for details.
>>>>>>> 555e96a (README file and some code were modified)
