# nadi-dashboard

**A web UI for Nadiru. Chat with AI, watch routing decisions in real time, track session costs.**

This is the most polished Nadi in the collection and the best demo of what Nadiru does. Open it in a browser, send a few prompts, and you'll see the routing pills change as the Conductor picks different models for different tasks. Click a pill to see the full reasoning. The insights panel tracks cost as you go. It's the visualization that makes Nadiru's value obvious.

## Usage

1. Make sure the Nadiru engine is running on `localhost:8765`
2. Open `index.html` in your browser

That's it. No build step, no `npm install`, no dependencies to manage. It's a single HTML file that loads React from a CDN.

## What you'll see

Three panels:

- **Chat** in the center. Send prompts, get responses with markdown rendering and code highlighting.
- **Insights** on the right. Live session cost, model usage breakdown, free-vs-paid split.
- **Routing feed** below the insights. Every interaction with the model that handled it and a click-to-expand reasoning.

The wow moment is sending three different prompts (a math question, a code request, a creative writing prompt) and watching the routing feed show three different models. That's Nadiru working as advertised.

## How it uses Nadiru

Talks to the engine's REST API directly from the browser using `fetch`. Uses `/connect`, `/generate/stream` (for streaming responses), `/query` (for the routing feed), and `/providers` (to populate the model dropdown). The streaming endpoint is particularly nice in the UI because you see the routing decision arrive first, then tokens flow in afterward.

If you've ever wondered "what does it actually look like to use Nadiru," this is the answer.

## Architecture

Single HTML file, single JSX file. React via CDN. Talks to the engine's REST API directly. No backend needed for the dashboard itself, the engine is the backend.

## Requirements

- Nadiru engine running on `localhost:8765`
- Modern browser (Chrome, Firefox, Edge)

## License

MIT, see [LICENSE](../LICENSE) in the parent repo.