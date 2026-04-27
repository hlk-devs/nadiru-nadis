# nadi-health

**Test every configured provider, report status and latency for each.**

A diagnostic Nadi for verifying your engine setup. Sends a tiny prompt through Nadiru with explicit provider targeting for each configured provider, then reports who responded, how long they took, and whether the request actually got routed where requested or got rerouted (which can happen if the engine considers the target unhealthy).

Run this after any config change to make sure all your provider keys are still working.

## Usage
