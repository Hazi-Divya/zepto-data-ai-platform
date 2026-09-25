# Zepto Data & AI Platform

An end-to-end AI/ML engineering capstone that combines three connected capabilities:

1. **Data Engineering** — scrape, clean, convert, store, and query catalog data.
2. **Analytics & Machine Learning** — explore, preprocess, model, evaluate, and build reproducible Titanic analysis pipelines.
3. **GenAI Support Assistant** — retrieve Zepto policy information from local documents and expose a grounded support API.

All three modules are maintained in a single repository.

---

## Project Structure

```text
zepto-data-ai-platform/
│
├── README.md
├── requirements.txt
│
├── data_pipeline/
│   ├── scraper.py
│   ├── cleaner.py
│   ├── database.py
│   ├── queries.py
│   ├── pandas_analysis.py
│   ├── run_pipeline.py
│   ├── README.md
│   ├── requirements.txt
│   ├── data/
│   ├── database/
│   └── outputs/
│
├── analytics/
│   ├── 01_eda.ipynb
│   ├── 02_modeling.ipynb
│   ├── titanic.csv
│   ├── best_pipeline.joblib
│   ├── requirements.txt
│   ├── README.md
│   └── outputs/
│
└── support_assistant/
    ├── docs/
    ├── chroma_db/
    ├── ingestion.py
    ├── graph.py
    ├── models.py
    ├── prompts.py
    ├── main.py
    ├── Dockerfile
    ├── requirements.txt
    └── README.md
```

---

# 1. Project Setup

This project uses **separate `requirements.txt` files for each module** because each module has different dependencies.

## Python Environment

Python 3.12+ is recommended.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

---

# 2. Module 1 — Data Pipeline

## Purpose

The Data Pipeline demonstrates a complete raw-to-relational workflow:

```text
Books to Scrape
      ↓
Web Scraping
      ↓
Raw CSV
      ↓
Data Cleaning
      ↓
GBP → INR Conversion
      ↓
Normalized SQLite Database
      ↓
SQL Analysis
      ↓
Pandas Analysis
```

The module uses:

* `requests`
* `BeautifulSoup`
* `pandas`
* `sqlite3`

## Data Source

The source is **Books to Scrape**:

```text
https://books.toscrape.com/
```

The scraper automatically discovers categories and follows pagination.

The final dataset contains:

* **69 books**
* **3 categories**

Each book contains:

* `title`
* `price_gbp`
* `rating`
* `availability`
* `category`

## Data Cleaning

The pipeline:

* removes currency symbols from prices
* converts prices to `float`
* converts textual ratings (`One`–`Five`) to integers `1`–`5`
* converts availability into a Boolean `in_stock`
* uses median imputation for numeric parsing failures
* drops rows with invalid availability, title, or category values

## Currency Conversion

The project-defined fixed conversion rate is:

```text
1 GBP = 105.50 INR
```

No external currency API is required.

```text
price_inr = price_gbp × 105.50
```

## SQLite Database

The database uses two related tables:

```text
categories
------------
category_id (PK)
category_name (UNIQUE)

books
------------
book_id (PK)
title
price_gbp
price_inr
rating
in_stock
category_id (FK)
```

The relationship is:

```text
categories 1 ───────── N books
```

Foreign-key validation is performed during the pipeline.

## SQL Analysis

Seven SQL queries are executed.

They collectively demonstrate:

* `SELECT`
* `WHERE`
* `ORDER BY`
* `LIMIT`
* `DISTINCT`
* `BETWEEN`
* `IN`
* `INNER JOIN`

SQL queries and their outputs are saved to:

```text
data_pipeline/outputs/sql_results.txt
```

## Pandas Analysis

The pipeline uses:

```python
pd.read_sql()
```

to read SQL results into DataFrames.

The SQL `JOIN` is independently reproduced using:

```python
pd.merge()
```

The SQL and Pandas results are compared for equivalence.

The comparison is saved to:

```text
data_pipeline/outputs/pandas_comparison.csv
```

## Module 1 Installation

From the project root:

```bash
pip install -r data_pipeline/requirements.txt
```

## Run Module 1

From the project root:

```bash
python data_pipeline/run_pipeline.py
```

The complete pipeline runs without manual copy/paste.

## Module 1 Results

| Check                |             Result |
| -------------------- | -----------------: |
| Books scraped        |                 69 |
| Categories           |                  3 |
| Cleaned records      |                 69 |
| GBP → INR rate       | 1 GBP = 105.50 INR |
| SQLite categories    |                  3 |
| SQLite books         |                 69 |
| Orphaned records     |                  0 |
| SQL queries          |                  7 |
| SQL/Pandas JOIN      |         Equivalent |
| End-to-end execution |         Successful |

Detailed Module 1 documentation is available in:

```text
data_pipeline/README.md
```

---

# 3. Module 2 — Analytics & Machine Learning

## Purpose

The Analytics module demonstrates an end-to-end data analytics and machine-learning workflow using the Titanic dataset.

The workflow covers:

```text
Titanic Dataset
      ↓
Data Audit
      ↓
Missing-Value Analysis
      ↓
Univariate Analysis
      ↓
Bivariate Analysis
      ↓
Correlation Analysis
      ↓
Multivariate Analysis
      ↓
Exploratory Standardization
      ↓
Train/Test Split
      ↓
Preprocessing Pipeline
      ↓
Classification Models
      ↓
Model Evaluation
      ↓
Imbalance Handling
      ↓
Random Forest Grid Search
      ↓
Regression
      ↓
Final Model Pipeline
```

## Dataset

The Titanic dataset is obtained using:

```python
sns.load_dataset("titanic")
```

The dataset is saved as:

```text
analytics/titanic.csv
```

The committed CSV acts as the offline fallback.

## Exploratory Data Analysis

The module includes:

* `df.info()`
* `df.describe()`
* `df.shape`
* missing-value percentages
* missing-value handling based on the required thresholds
* age histogram
* fare histogram
* age boxplot
* fare boxplot
* IQR-based outlier detection
* fare mean, median, mode, and skewness
* survival analysis by sex
* survival analysis by passenger class
* survival analysis by sex and passenger class

## Correlation Analysis

The required correlation variables are:

```text
survived
pclass
age
sibsp
parch
fare
```

A correlation heatmap is created and the two largest absolute off-diagonal correlations are interpreted.

## Multivariate Analysis

The analysis contains multiple distinct visualizations with written interpretations explaining the observed relationships.

## Exploratory Standardization

`age` and `fare` are standardized for exploratory analysis.

The standardized values are not used as input to the final modeling pipeline.

## Classification

The modeling workflow uses:

* Logistic Regression
* Decision Tree
* Random Forest

A stratified train/test split is used before preprocessing.

Preprocessing is performed through:

```text
ColumnTransformer
        +
Pipeline
```

The preprocessing includes:

* missing-value handling
* categorical encoding
* numerical standardization

## Model Evaluation

The classifiers are evaluated using:

* confusion matrix
* accuracy
* precision
* recall
* F1-score
* ROC curve
* AUC

A comparison table is produced.

## Class Imbalance

The module compares:

1. baseline classifier
2. `class_weight="balanced"`
3. SMOTE applied only to training data

Precision, recall, and F1-score are compared.

## Random Forest Tuning

`GridSearchCV` is used to tune:

* `n_estimators`
* `max_depth`
* `max_features`

The Random Forest estimator uses:

```python
oob_score=True
```

The best parameters and OOB score are reported.

## Regression

A multivariate linear regression model predicts:

```text
fare
```

using other available features.

The regression evaluation includes:

* MAE
* RMSE
* R²
* Adjusted R²
* residual plot
* heteroscedasticity interpretation

Classifier and regression metrics are reported separately.

## Model Persistence

The complete fitted classification pipeline, including preprocessing and estimator, is saved using:

```python
joblib.dump()
```

The saved pipeline is reloaded and tested using raw input data.

## Module 2 Installation

From the project root:

```bash
pip install -r analytics/requirements.txt
```

## Run Module 2

Open:

```text
analytics/01_eda.ipynb
analytics/02_modeling.ipynb
```

Run the notebooks from top to bottom.

Detailed Module 2 documentation is available in:

```text
analytics/README.md
```

---

# 4. Module 3 — GenAI Support Assistant

## Purpose

The Support Assistant demonstrates a locally grounded GenAI support system for Zepto policy questions.

The architecture is:

```text
Policy Documents
      ↓
Document Ingestion
      ↓
Local Embeddings
      ↓
ChromaDB
      ↓
User Query
      ↓
LangGraph Intent Classification
      ↓
Policy Retrieval / Direct Answer
      ↓
Response Generation
      ↓
Pydantic Validation
      ↓
FastAPI
```

## Policy Documents

The assistant uses eight supplied policy documents:

1. Delivery Policy
2. Returns & Refunds
3. Membership Tiers
4. Order Tracking
5. Order Cancellation Policy
6. Damaged or Missing Items
7. Gift Cards
8. Customer Support Hours

The documents are stored locally under:

```text
support_assistant/docs/
```

## Embeddings

The project uses the local:

```text
sentence-transformers
all-MiniLM-L6-v2
```

No paid embedding API is required.

## Vector Database

ChromaDB is used as the local vector database.

Policy questions retrieve the top 3 relevant chunks using cosine similarity.

## Prompt Structure

The prompt follows:

```text
Role
Context
Task
Format
Length
```

The prompt also explicitly prevents unsupported answers:

```text
Do not answer using information not present in the provided context.
```

A few-shot example is included in the prompt.

## LangGraph

The assistant uses a LangGraph `StateGraph` with the following nodes:

```text
classify_intent
       ↓
   ┌───┴────┐
   ↓        ↓
retrieve   direct
_and       _answer
answer
```

The classifier identifies policy-related questions such as:

* delivery
* return
* refund
* membership
* tracking
* cancellation
* gift card
* support hours

Other questions are routed to the general-answer path.

## Mock LLM Mode

The required baseline works without a paid LLM provider.

The environment variable is:

```text
MOCK_LLM
```

Default behavior:

```text
MOCK_LLM unset or 1 → deterministic mock mode
MOCK_LLM=0          → optional real LLM mode
```

In mock mode, policy questions still perform embedding and top-3 ChromaDB retrieval.

The mock response contains:

* deterministic answer
* retrieved source IDs
* confidence score

General questions return a deterministic response indicating that the assistant currently answers Zepto policy questions only.

## Response Validation

Responses use Pydantic validation:

```text
answer: str
sources: list
confidence: float
```

Confidence is restricted to the range:

```text
0–1
```

The optional real-LLM path validates generated output and retries invalid responses up to two additional times.

## FastAPI

The assistant exposes:

```text
POST /ask
```

Example request:

```json
{
  "query": "What is the delivery policy?"
}
```

The response follows the Pydantic response schema.

The API is served using Uvicorn.

## Module 3 Installation

From the project root:

```bash
pip install -r support_assistant/requirements.txt
```

## Run Module 3

From the project root:

```bash
cd support_assistant
```

Then:

```bash
uvicorn main:app --host 0.0.0.0 --port 7860
```

The required baseline works with `MOCK_LLM=1` or when `MOCK_LLM` is unset.

## Docker

The module also contains:

```text
support_assistant/Dockerfile
```

for local containerized execution.

Detailed Module 3 documentation is available in:

```text
support_assistant/README.md
```

---

# 5. Overall Design Decisions

## Modular Architecture

Each capability is isolated inside its own module:

```text
data_pipeline/
analytics/
support_assistant/
```

This keeps data engineering, machine learning, and GenAI functionality independently executable while maintaining a single repository.

## Reproducibility

The project favors reproducible workflows through:

* fixed GBP → INR conversion
* SQLite database recreation
* saved datasets
* saved SQL outputs
* saved model pipeline
* deterministic mock LLM mode
* local embeddings and ChromaDB

## No Paid Services

The required implementation does not depend on paid external services.

The Data Pipeline uses a public scraping-practice website and a fixed project-defined currency conversion rate.

The Support Assistant provides a deterministic `MOCK_LLM` baseline and local embeddings.

---

# 6. Git Workflow

The repository follows the required feature-branch workflow.

A feature branch was created for the Data Pipeline:

```text
feature/data-pipeline
```

The branch received multiple commits before being merged back into `main`.

The history can be inspected using:

```bash
git log --graph --all --oneline
```

The workflow demonstrates:

```text
main
  │
  └── feature/data-pipeline
          │
          ├── commit 1
          ├── commit 2
          │
          └──────────────► merge back to main
```

---

# 7. Running the Project

## Module 1 — Data Pipeline

```bash
pip install -r data_pipeline/requirements.txt
python data_pipeline/run_pipeline.py
```

## Module 2 — Analytics

```bash
pip install -r analytics/requirements.txt
```

Then open and run:

```text
analytics/01_eda.ipynb
analytics/02_modeling.ipynb
```

## Module 3 — Support Assistant

```bash
pip install -r support_assistant/requirements.txt
cd support_assistant
uvicorn main:app --host 0.0.0.0 --port 7860
```

---

# 8. Module Documentation

Each module contains additional implementation-specific documentation:

```text
data_pipeline/README.md
analytics/README.md
support_assistant/README.md
```

These files contain detailed implementation notes, outputs, analysis, and design decisions for their respective modules.

---

# 9. Repository Submission

The complete project is submitted as **one public GitHub repository**.

Repository structure:

```text
zepto-data-ai-platform/
├── README.md
├── data_pipeline/
├── analytics/
└── support_assistant/
```

The repository contains all three capabilities required for the Zepto Data & AI Platform capstone.

---

# 10. Final Architecture

```text
                    ZEPTO DATA & AI PLATFORM
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
      DATA PIPELINE       ANALYTICS       SUPPORT ASSISTANT
             │                │                │
             ▼                ▼                ▼
      Web Scraping        EDA + ML        Policy Documents
             │                │                │
             ▼                ▼                ▼
      Data Cleaning       Modeling       Local Embeddings
             │                │                │
             ▼                ▼                ▼
      SQLite Database     Evaluation        ChromaDB
             │                │                │
             ▼                ▼                ▼
       SQL + Pandas       Joblib Model      LangGraph
                                              │
                                              ▼
                                           FastAPI
```

This project demonstrates an end-to-end AI/ML engineering workflow covering **data engineering, analytics and machine learning, and grounded GenAI application development**.
