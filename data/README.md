# Data folder

This folder holds the car information used by the learning project.

## What is `cars.json`?

`cars.json` is a JSON array of about 30 Indian-market cars (demo / learning data).

Each car has the same field names so the backend and frontend can rely on a consistent shape.

**Important:** Prices, mileage, specs, and safety ratings are **representative demo values**, not live market figures.

## Why JSON first?

JSON is simple to read and edit. For learning RAG, it is enough to:

1. Store structured car facts in a file.
2. Later convert each car into text documents.
3. Create embeddings and store them in ChromaDB.
4. Retrieve relevant cars and ask Gemini to answer.

No database is needed at this stage.

## Structured vs descriptive fields

### Structured (good for exact filters)

| Field | Example |
|-------|---------|
| `price` | `1450000` |
| `fuel_type` | `"Petrol"` |
| `transmission` | `"Automatic"` |
| `body_type` | `"Compact SUV"` |
| `mileage` | `17.0` |
| `seating_capacity` | `5` |
| `brand`, `model`, `variant` | `"Tata"`, `"Nexon"`, `"Creative+"` |
| `safety_rating` | `5` |

These support queries like: “petrol automatic under 15 lakh”.

### Descriptive (good for meaning / later semantic search)

| Field | Example |
|-------|---------|
| `description` | Short paragraph about the car |
| `suitable_for` | `["Family", "City Driving"]` |
| `features` | Infotainment, sunroof, etc. |
| `safety_features` | Airbags, ABS, ESC, etc. |

These help answer questions like: “good for a family of 5” or “which car has good safety features?”

## How this data will be used by RAG (future steps)

```
cars.json
  ↓
turn each car into text documents
  ↓
create embeddings (Gemini embedding model)
  ↓
store vectors in ChromaDB
  ↓
semantic retrieval for a user question
  ↓
Gemini generates a natural-language answer
```

In Step 2 we only **read and filter** this JSON. Embeddings and ChromaDB come later.
