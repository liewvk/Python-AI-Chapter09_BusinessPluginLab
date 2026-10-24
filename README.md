# Business Plugin Lab

This repository contains a small Python demo built with Semantic Kernel for a business assistant that can work with plugin-based tools for product catalog lookup, pricing, discount logic, order status, and AI-assisted explanations.

The sample is intended for learning how to connect a local AI model to structured business functions and expose them through a command-line workflow.

## What this project does

The application provides a menu-driven business console with the following capabilities:

- List registered plugin functions
- Show sample products
- Retrieve product information
- Calculate a purchase total
- Apply a discount
- Check a sample order status
- Generate a quotation
- Explain the latest result with AI

## Project structure

- `main.py` — menu-driven console app and orchestration logic
- `business_plugins.py` — business plugin functions for catalog, pricing, discounts, and orders
- `kernel_service.py` — Semantic Kernel service and plugin registration
- `settings.py` — model and API configuration
- `requirements.txt` — Python dependencies

## Requirements

- Python 3.10+
- An Ollama instance running locally
- The model configured in `settings.py` (`qwen3.5:9b`)

## Setup

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start Ollama and ensure the model is available:

   ```bash
   ollama pull qwen3.5:9b
   ```

4. Run the application:

   ```bash
   python main.py
   ```

## Configuration

The application uses a local OpenAI-compatible endpoint configured in `settings.py`:

```python
OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL_NAME = "qwen3.5:9b"
```

## Example workflow

After launching the script, the app displays a menu with business actions. You can:

- inspect the registered plugins,
- lookup product prices and stock,
- calculate totals with quantities,
- apply discounts,
- review sample order status,
- ask the AI to explain the latest result in natural language.

## Notes

This project is a learning demo and uses sample product and order data rather than a real business system database.

## License

This project does not currently declare an explicit license file.
