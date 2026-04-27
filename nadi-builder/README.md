# nadi-builder

**Build new Nadis by describing what you want. Two AI providers collaborate: one writes the code, a different one independently reviews it.**

This Nadi shows off something interesting about Nadiru: because the engine talks to multiple providers, you can run multi-provider workflows where different models check each other's work. The writer and reviewer always come from different providers, which means they have different training data, different blind spots, and different biases. You get genuinely independent code review built into the generation step.

## Usage

1. Make sure the Nadiru engine is running on `localhost:8765`
2. Open `index.html` in your browser
3. Describe your Nadi in plain English ("a Nadi that takes a YouTube URL and summarizes the transcript")
4. Watch it write, review, and revise

The final output is a Python script you can save and run.

## What you'll see

A three-panel UI: your description on the left, the writer's first draft in the middle, the reviewer's feedback and final corrected code on the right. Each panel shows which provider and model handled that step. You'll see the writer make a mistake, the reviewer catch it, and the final code reflect the fix.

The interesting moment is when you watch a model from one provider point out a real bug in code written by a model from another provider. That's not something you get from a single-provider workflow.

## How it uses Nadiru

Calls `/generate` twice with `priority: "quality"`. The first call generates code. The second call sends the generated code back through the engine for review, but with a system prompt that biases the Conductor toward a different provider than the one used in the first call. The result is two independent perspectives on the same problem in a single workflow.

This pattern (multi-provider review pipelines) is one of the more useful things Nadiru enables. See also `nadi-deepreview` for a three-stage version applied to existing code.

## Requirements

- Nadiru engine running on `localhost:8765`
- At least 2 paid providers configured (so writer and reviewer can come from different sources)
- Modern browser

## License

MIT, see [LICENSE](../LICENSE) in the parent repo.