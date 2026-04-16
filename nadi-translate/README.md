# nadi-translate

Translate text between languages using the Nadiru engine.

## Usage

```bash
python translate.py "Hello, how are you?" spanish
python translate.py "Bonjour le monde" english
python translate.py --file document.txt japanese
```

## How it works

A single-purpose Nadi that sends a translation prompt to the engine. The Conductor picks the best model for the task — translation often routes to cost-effective models since most handle it well.

This Nadi demonstrates the pattern for building simple, focused tools on Nadiru: connect, send a structured prompt, display the result.

## Requirements

- Nadiru engine running on `localhost:8765`
- `pip install httpx`
