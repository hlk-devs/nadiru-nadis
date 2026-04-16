# nadi-summarize

Summarize text using the Nadiru engine.

## Usage

```bash
python summarize.py "Your long text to summarize goes here"
python summarize.py --file article.txt
python summarize.py --file article.txt --length short
python summarize.py --file article.txt --length detailed
```

## Length options

- `short` — 1-2 sentences
- `concise` — short paragraph (default)
- `detailed` — comprehensive summary

## How it works

Routes with `priority: cost` since summarization works well on cheaper models. The Conductor will typically pick a cost-effective model for this task type.

## Requirements

- Nadiru engine running on `localhost:8765`
- `pip install httpx`
