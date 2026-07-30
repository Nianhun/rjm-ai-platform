# Formula Element Graph Design

## Goal

Add an independent "formula element analysis" page to the engineer console. A formulator can enter a Yuxi element ID such as `YUXI-A0F1011EC3C6A15ED4DB23D0BD8575A5` and inspect a one-hop knowledge graph centered on that element.

## User Experience

The page is a first-class workspace view in the left rail. It has a compact search bar at the top, a large graph canvas below it, and a detail panel for the center or selected node.

The initial state shows an empty graph area with a focused input. After the user searches:

- The queried element appears as the large center node.
- Directly connected one-hop nodes are arranged around it.
- Edges connect neighbors to the center or to any included one-hop relationships returned by Yuxi.
- Edge labels show a short relation type when available.
- A small stats block shows node count and edge count.
- Clicking a node updates the detail panel with ID, label, type, description, and raw metadata when useful.

## Architecture

Use the existing request chain:

`engineer console -> Java management API -> Python AI engine -> Yuxi graph API`

This keeps browser authentication and API token handling in the existing Java service and avoids exposing Yuxi credentials to the frontend.

## Backend API

Add Java endpoint:

`GET /api/knowledge/elements/{elementId}/graph`

The Java service delegates to Python:

`GET /knowledge/elements/{element_id}/graph`

Python calls the configured Yuxi graph gateway using the current KB ID, `max_depth=1`, and a bounded `max_nodes` value. The response is normalized for UI rendering:

```json
{
  "query": "YUXI-A0F1011EC3C6A15ED4DB23D0BD8575A5",
  "center": {
    "id": "YUXI-A0F1011EC3C6A15ED4DB23D0BD8575A5",
    "label": "Sodium Hyaluronate",
    "type": "Ingredient",
    "description": "..."
  },
  "nodes": [
    {
      "id": "YUXI-A0F1011EC3C6A15ED4DB23D0BD8575A5",
      "label": "Sodium Hyaluronate",
      "type": "Ingredient",
      "description": "...",
      "properties": {}
    }
  ],
  "edges": [
    {
      "id": "rel-1",
      "source": "YUXI-A0F1011EC3C6A15ED4DB23D0BD8575A5",
      "target": "YUXI-OTHER",
      "label": "co_occurrence",
      "type": "co_occurrence"
    }
  ],
  "stats": {
    "node_count": 1,
    "edge_count": 0,
    "truncated": false
  }
}
```

## Error Handling

If Yuxi graph is disabled or unavailable, return a service-level error that the UI displays as "Yuxi knowledge graph is unavailable."

If no center node or one-hop graph is found, return an empty graph response with `center` omitted and `stats.node_count=0`; the UI displays "No element or one-hop relations found."

If Yuxi returns more than the UI limit, Python truncates to the configured maximum and sets `stats.truncated=true`.

## Frontend Rendering

Use native SVG so the feature has no new dependency. The graph renderer is deterministic:

- Center node at the midpoint.
- One-hop neighbors placed evenly on a circle.
- Neighbor color is based on node type.
- Center node is larger and uses the current product accent color.
- Labels use compact text with SVG `<title>` for full labels.
- The SVG scales to desktop and mobile widths without overlapping the surrounding UI.

This is sufficient for the requested one-hop view and can later be replaced by a force-directed library if multi-hop graph exploration becomes necessary.

## Tests

Python:

- Gateway-backed service returns normalized one-hop graph.
- Missing or unavailable graph returns the expected error or empty response.

Java:

- Client delegates `/knowledge/elements/{id}/graph` to Python.
- Controller exposes `/api/knowledge/elements/{id}/graph`.

Frontend:

- `node --check` verifies JavaScript syntax.
- A targeted DOM smoke test verifies the new page, input, search action, SVG graph container, and empty state text.

## Out Of Scope

- Multi-hop expansion from clicked nodes.
- Graph editing.
- Persisted graph search history.
- Direct Yuxi calls from the browser.
