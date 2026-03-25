# Data Engineering Case

## Case Study: Data Engineer @ Allrecipes

Congratulations on being appointed as a Data Engineer. As part of your new role, you are tasked with creating a working
proof-of-concept (PoC) to enhance recipe data intelligence.

---

## Project Goals

Develop a Python-based API that helps:

- Identify ingredient patterns
- Manage content quality

---

## Task 1: Ingredient Co-occurrence (Required)

**Goal:** Identify ingredients commonly used together.

- **Requirement:**  
  Provide a top 10 list of ingredients most frequently paired with a specified input (e.g., "cinnamon").

- **Focus Areas:**
    - Data aggregation
    - Relationship mapping

---

## Task 2: Duplicate Identification (Optional)

**Goal:** Identify possible duplicate recipes when new ones are uploaded.

- **Requirement:**  
  Return a top 5 list of similar recipes along with a similarity score.

- **Focus Areas:**
    - Pattern matching
    - Text similarity

---

## Technical Requirements

- **Language:** Python
- **Frameworks:** You may choose any tools or frameworks (e.g., FastAPI, Flask, Pandas)
- **Evaluation Criteria:** Focus on design decisions and methodology. The rationale behind your approach is as important
  as the implementation.

---

## Data Sources

- Dataset: http://allrecipes.com/
- Download:  
  https://rotate-storage-5c2dcb0290500-production.s3.eu-central-1.amazonaws.com/public/recruitment/data_engineer_challange/recipe_database.zip

---

## API Specification Examples

### Task 1: Ingredient Co-occurrence

**Endpoint:**
```

GET /api/ingredient-cooccurrence?ingredient=cinnamon

````

**Success Response:**
```json
{
  "ingredient": "cinnamon",
  "cooccurrence": [
    { "ingredient": "sugar", "count": 2384 },
    { "ingredient": "nutmeg", "count": 1231 },
    { "ingredient": "vanilla extract", "count": 981 }
  ]
}
````

---

### Task 2: Recipe Duplicates

**Endpoint:**

```
POST /api/recipe-duplicates
```

**Payload:**

```json
{
  "recipe": {
    "name": "Cinnamon Bun Bread",
    "ingredients": [
      {
        "name": "all-purpose flour",
        "quantity": "3 cups"
      },
      {
        "name": "baking powder",
        "quantity": "1 tablespoon"
      }
    ]
  }
}
```

**Success Response:**

```json
{
  "duplicates": [
    {
      "name": "Cinnamon Swirl Bread",
      "similarity": 0.94
    },
    {
      "name": "Cinnamon Raisin Bread",
      "similarity": 0.87
    }
  ]
}
```

---

## Contact Information

* [hans@letsrotate.com](mailto:hans@letsrotate.com)
* [thomas@letsrotate.com](mailto:thomas@letsrotate.com)

