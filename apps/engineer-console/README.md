# Engineer Console

## Responsibility

Static single-page engineer workbench for recommendation review, screening, experiment feedback, procurement, knowledge status, evidence lookup, and learning explanations.

## Tech Stack

- HTML
- CSS
- Vanilla JavaScript

## Structure

```text
index.html
styles.css
app.js
README.md
```

## Start

Preferred local stack:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_demo.ps1 -UseYuxiKnowledge
```

Then open:

```text
http://127.0.0.1:8080/console/
```

Direct file inspection is also possible:

```text
F:\zky\RJM\apps\engineer-console\index.html
```

Legacy path remains available:

```text
F:\zky\RJM\ui\engineer-console\index.html
```

## Test

```powershell
node --check apps\engineer-console\app.js
```

## API Dependency

The console calls the Java management API under `/api/**`. It does not call the Python AI service directly in the normal stack.
