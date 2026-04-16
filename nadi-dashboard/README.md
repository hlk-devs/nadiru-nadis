# nadi-dashboard

Web interface for the Nadiru engine. Chat with AI, see routing decisions in real time, track costs.

## Usage

1. Make sure the Nadiru engine is running on `localhost:8765`
2. Open `index.html` in your browser

That's it. No build step, no npm install, no dependencies to manage.

## Features

- Full chat interface with markdown rendering and code highlighting
- Live routing indicators showing which model handled each response
- Click any routing pill to see the full routing reasoning
- Priority selector (cost / balanced / quality)
- Insights panel with session cost tracking and model usage breakdown
- Real-time routing feed showing all interactions

## Architecture

Single HTML file. Uses React via CDN for interactivity. Talks to the engine's REST API directly from the browser. No backend needed for the dashboard itself.

## Requirements

- Nadiru engine running on `localhost:8765`
- Modern browser (Chrome, Firefox, Edge)
