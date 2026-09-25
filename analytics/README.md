# Module 2 — Analytics Pipeline

## Overview

This module implements an end-to-end **Titanic analytics and predictive modeling pipeline** using Python, pandas, seaborn, scikit-learn, imbalanced-learn, matplotlib, and joblib.

The workflow covers:

1. Dataset loading and profiling
2. Missing-value handling
3. Exploratory Data Analysis (EDA)
4. Univariate, bivariate, and multivariate analysis
5. EDA standardization sanity check
6. Classification modeling
7. Class-imbalance analysis
8. Random Forest hyperparameter tuning
9. Multivariate linear regression for fare prediction
10. Final model comparison
11. Saving and reloading the complete trained pipeline

The raw Titanic dataset is loaded through Seaborn once in `01_eda.ipynb`. The exact loaded dataset is saved as `titanic.csv` and reused by `02_modeling.ipynb`. This makes the modeling stage reproducible without requiring another network download.

---

## Project Structure

```text
analytics/
├── 01_eda.ipynb
├── 02_modeling.ipynb
├── titanic.csv
├── requirements.txt
├── README.md
│
├── models/
│   └── best_tuned_random_forest_pipeline.joblib
│
└── outputs/
    ├── multivariate_01_survival_sex_class.png
    ├── multivariate_02_age_fare_survival.png
    ├── multivariate_03_fare_class_survival.png
    ├── multivariate_04_sibsp_class_survival.png
    └── regression_residual_plot.png
```

---

# Part A — Profiling, Cleaning and EDA

## 1. Dataset Loading and Profiling

The classic Titanic dataset was loaded using Seaborn:

```python
sns.load_dataset("titanic")
```

The loaded dataset contains:

- **Rows:** 891
- **Columns:** 15

The exact loaded DataFrame was then saved locally:

```python
df.to_csv("titanic.csv", index=False)
```

The CSV provides an offline copy of the source dataset.

The modeling notebook reads this committed CSV instead of independently loading the Titanic dataset from the network.

---

## 2. Missing-Value Analysis

The following columns contained missing values:

| Column | Missing Count | Missing Percentage | Strategy |
|---|---:|---:|---|
| `age` | 177 | 19.87% | Median imputation |
| `embarked` | 2 | 0.22% | Drop affected rows |
| `deck` | 688 | 77.22% | Drop column |
| `embark_town` | 2 | 0.22% | Drop affected rows |

### Missing-Value Rule

The following threshold rule was used:

- **Less than 5% missing:** Drop affected rows
- **5%–30% missing:** Impute missing values
- **Very high missingness:** Drop the column when reliable imputation is not appropriate

The `deck` column had **77.22% missing values**, so it was dropped.

After cleaning, the dataset contained:

- **889 rows**
- **14 columns**

---

## 3. Univariate Analysis

### Age

The age distribution was analyzed using summary statistics and outlier detection.

- **Q1:** 22.0
- **Q3:** 35.0
- **IQR:** 13.0
- **IQR outliers:** 65

The age distribution is concentrated mainly between 20 and 40 years.

### Fare

Fare was also analyzed using summary statistics and the IQR method.

- **Mean:** 32.0967
- **Median:** 14.4542
- **Mode:** 8.05
- **IQR outliers:** 114

Since:

**Mean > Median > Mode**

the fare distribution is **right-skewed**.

The histogram and box plot also show a smaller number of unusually high fares.

---

## 4. Bivariate Analysis

### Survival Rate

| Group | Survival Rate |
|---|---:|
| Female | 74.04% |
| Male | 18.89% |
| 1st Class | 62.62% |
| 2nd Class | 47.28% |
| 3rd Class | 24.24% |

### Survival by Sex and Passenger Class

| Group | Survival Rate |
|---|---:|
| Female, 1st class | 96.74% |
| Female, 2nd class | 92.11% |
| Female, 3rd class | 50.00% |
| Male, 1st class | 36.89% |
| Male, 2nd class | 15.74% |
| Male, 3rd class | 13.54% |

Boolean masking using `&` and `|` was also used for combined filtering conditions.

### Correlation Analysis

The correlation matrix used the following variables:

```text
survived
pclass
age
sibsp
parch
fare
```

The two strongest absolute correlations were:

- `pclass` and `fare`: **-0.5482**
- `sibsp` and `parch`: **0.4145**

The columns `adult_male` and `alone` were excluded because they are derived/redundant flags.

---

## 5. Multivariate Data Story

Four charts were created to examine survival using multiple passenger characteristics.

### 1. Survival by Sex and Class

Survival varies by both sex and passenger class. Female passengers generally had higher survival rates than male passengers within the same class, while higher-class passengers also showed higher survival in several groups.

### 2. Age, Fare and Survival

Fare is concentrated at lower values, while some passengers paid much higher fares. Survival varies across different age and fare combinations, showing that age or fare alone does not fully explain the observed outcomes.

### 3. Fare by Class and Survival

Higher passenger classes generally have higher fares, with several high-fare outliers. Survival also varies within each class, indicating that passenger class and fare are related to the observed survival patterns.

### 4. Survival by Siblings/Spouses and Class

Survival patterns vary with the number of siblings or spouses and passenger class. Passenger class continues to distinguish survival patterns across different family-group sizes, showing the value of considering multiple characteristics together.

---

## 6. EDA Standardization Sanity Check

Age and fare were standardized using **z-score standardization**.

| Feature | Before Mean | Before Std |
|---|---:|---:|
| Age | 29.3152 | 12.9849 |
| Fare | 32.0967 | 49.6975 |

After standardization, both features had means approximately **0** and standard deviations approximately **1**.

This confirms that the standardization worked correctly.

> **Note:** This standardization step was used only for EDA validation and was not used directly in the modeling pipeline.

---

# Part B — Predictive Modeling

## 7. Classification Setup

The target variable was:

```text
survived
```

### Features

The following features were used:

```text
pclass
sex
age
sibsp
parch
fare
embarked
```

The data was split using an **80/20 stratified train/test split**.

| Dataset | Samples |
|---|---:|
| Training | 711 |
| Testing | 178 |

### Target Distribution

| Class | Percentage |
|---|---:|
| Not Survived | 61.75% |
| Survived | 38.25% |

Stratification was used to preserve the class distribution in both the training and testing sets.

---

## 8. Preprocessing

A `ColumnTransformer` and `Pipeline` were used to keep preprocessing and model training consistent.

### Numeric Features

The numeric preprocessing pipeline used:

1. Median imputation
2. `StandardScaler`

### Categorical Features

The categorical preprocessing pipeline used:

1. Most-frequent imputation
2. One-hot encoding

Preprocessing was fitted on the training data and then applied to the test data to avoid test-set leakage.

---

## 9. Classification Models

Three baseline classifiers were trained using the same train/test split:

- Logistic Regression
- Decision Tree
- Random Forest

The Decision Tree was also visualized using `plot_tree` with feature and class names.

---

## 10. Classification Results

| Model | Accuracy | Precision | Recall | F1 | AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
| Decision Tree | 0.7697 | 0.6901 | 0.7206 | 0.7050 | 0.7541 |
| Random Forest | 0.8202 | 0.7812 | 0.7353 | 0.7576 | 0.8179 |
| Tuned Random Forest | 0.8315 | 0.8654 | 0.6618 | 0.7500 | 0.8389 |

Confusion matrices and ROC curves with AUC were generated for the three original classifiers.

---

## 11. Class Imbalance Experiment

Three Logistic Regression approaches were compared:

1. Baseline
2. Class weighting
3. SMOTE

| Strategy | Precision | Recall | F1 |
|---|---:|---:|---:|
| Baseline | 0.7833 | 0.6912 | 0.7344 |
| Class Weight = Balanced | 0.7183 | 0.7500 | 0.7338 |
| SMOTE | 0.7353 | 0.7353 | 0.7353 |

Observations from the experiment:

- The baseline produced the highest precision.
- Class weighting produced the highest recall.
- SMOTE produced the highest F1-score.
- The F1 differences were small.
- SMOTE provided the most balanced precision-recall result in this experiment.

SMOTE was applied only to the training data to avoid test-set leakage.

---

## 12. Random Forest Hyperparameter Tuning

`GridSearchCV` was used to tune:

- `n_estimators`
- `max_depth`
- `max_features`

### Best Parameters

```text
n_estimators = 200
max_depth = 5
max_features = sqrt
```

### Cross-Validation Result

**Best cross-validation F1-score:** 0.7408

**OOB score:** 0.8214

### Tuned Random Forest Test Results

| Metric | Value |
|---|---:|
| Accuracy | 0.8315 |
| Precision | 0.8654 |
| Recall | 0.6618 |
| F1 | 0.7500 |
| AUC | 0.8389 |

---

# Part C — Regression Side-Task

## 13. Multivariate Linear Regression

A multivariate Linear Regression model was used to predict `fare` from the available passenger features.

### Regression Results

| Metric | Value |
|---|---:|
| MAE | 18.3945 |
| RMSE | 41.3578 |
| R² | 0.3589 |
| Adjusted R² | 0.2679 |

The residual plot shows that the spread of residuals increases as predicted fare increases.

This provides evidence of **heteroscedasticity**, meaning that the residual variance is not constant.

---

# Part D — Final Comparison and Deployment

## 14. Final Classification Comparison

| Model | Accuracy | Precision | Recall | F1 | AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
| Decision Tree | 0.7697 | 0.6901 | 0.7206 | 0.7050 | 0.7541 |
| Random Forest | 0.8202 | 0.7812 | 0.7353 | 0.7576 | 0.8179 |
| Tuned Random Forest | 0.8315 | 0.8654 | 0.6618 | 0.7500 | 0.8389 |

### Regression Comparison

| MAE | RMSE | R² | Adjusted R² |
|---:|---:|---:|---:|
| 18.3945 | 41.3578 | 0.3589 | 0.2679 |

Classification and regression metrics are presented separately because they measure different types of predictive performance.

### Deployment Model

The tuned Random Forest was selected as the deployment model based on the evaluation criteria used in this project.

It achieved:

- **Accuracy:** 0.8315
- **Precision:** 0.8654
- **Recall:** 0.6618
- **F1:** 0.7500
- **AUC:** 0.8389

For comparison, Logistic Regression achieved an **AUC of 0.8610**, while the tuned Random Forest had a lower recall of **0.6618**.

The model selection therefore considered multiple evaluation metrics rather than relying on accuracy alone.

---

# Part E — Saved Model and Reproducibility

## 15. Saved Model

The complete tuned Random Forest pipeline, including preprocessing and the trained estimator, was saved using `joblib`.

Saved model:

```text
models/best_tuned_random_forest_pipeline.joblib
```

Saving the complete pipeline allows preprocessing and model inference to remain consistent when the trained model is reloaded.

---

# Part F — How to Run

## 16. Setup

From the project root, navigate to the analytics directory:

```powershell
cd analytics
```

### Create a Virtual Environment

If the virtual environment does not already exist:

```powershell
python -m venv .venv
```

### Activate the Virtual Environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you may need to adjust the execution policy for your user account before activating the environment.

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Start Jupyter Notebook

```powershell
jupyter notebook
```

---

## 17. Run the Notebooks in Order

Run the notebooks in the following order:

### Step 1 — EDA

```text
01_eda.ipynb
```

This notebook:

- Loads the Titanic dataset through Seaborn
- Profiles the dataset
- Performs missing-value analysis
- Cleans the data
- Performs univariate analysis
- Performs bivariate analysis
- Performs multivariate analysis
- Runs the EDA standardization sanity check
- Creates the EDA output charts
- Saves the exact dataset as `titanic.csv`

### Step 2 — Modeling

```text
02_modeling.ipynb
```

This notebook:

- Reads `titanic.csv`
- Preprocesses the features
- Trains the classification models
- Evaluates the classification models
- Performs the class-imbalance experiment
- Tunes the Random Forest using `GridSearchCV`
- Performs the regression side-task
- Generates the regression residual plot
- Saves the final trained pipeline

---

# Part G — Dependencies and Outputs

## 18. Dependencies

The required Python packages are listed in:

```text
requirements.txt
```

The project uses libraries for:

- Data manipulation
- Data visualization
- Statistical/EDA analysis
- Machine learning
- Imbalanced classification
- Model serialization
- Jupyter notebook execution

Install all required packages with:

```powershell
pip install -r requirements.txt
```

---

## 19. Generated Artifacts

### Dataset

```text
titanic.csv
```

An offline copy of the Titanic dataset loaded during the EDA stage.

### Visualizations

```text
outputs/
├── multivariate_01_survival_sex_class.png
├── multivariate_02_age_fare_survival.png
├── multivariate_03_fare_class_survival.png
├── multivariate_04_sibsp_class_survival.png
└── regression_residual_plot.png
```

### Trained Model

```text
models/best_tuned_random_forest_pipeline.joblib
```

The saved preprocessing + tuned Random Forest pipeline.

---

# 20. Reproducibility

The project is designed so that the EDA and modeling stages are separated while sharing the same committed dataset.

The reproducible workflow is:

```text
Seaborn Titanic Dataset
        │
        ▼
  01_eda.ipynb
        │
        ├── Profiling
        ├── Cleaning
        ├── EDA
        ├── Multivariate Analysis
        └── Standardization Check
        │
        ▼
   titanic.csv
        │
        ▼
  02_modeling.ipynb
        │
        ├── Preprocessing Pipeline
        ├── Classification
        ├── Imbalance Experiment
        ├── Random Forest Tuning
        ├── Regression
        └── Model Evaluation
        │
        ▼
best_tuned_random_forest_pipeline.joblib
```

---

# 21. Verification

The analytics pipeline was verified after execution.

The module contains:

- EDA notebook
- Modeling notebook
- Committed Titanic dataset
- Generated visualization outputs
- Trained Random Forest pipeline
- Requirements file
- Project documentation

The notebooks contain the detailed analysis, interpretations, model evaluation, and conclusions.

---

## Key Results at a Glance

### Classification

| Model | Accuracy | Precision | Recall | F1 | AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
| Decision Tree | 0.7697 | 0.6901 | 0.7206 | 0.7050 | 0.7541 |
| Random Forest | 0.8202 | 0.7812 | 0.7353 | 0.7576 | 0.8179 |
| Tuned Random Forest | **0.8315** | **0.8654** | 0.6618 | 0.7500 | 0.8389 |

### Regression

| Metric | Value |
|---|---:|
| MAE | 18.3945 |
| RMSE | 41.3578 |
| R² | 0.3589 |
| Adjusted R² | 0.2679 |

---

## Conclusion

This module demonstrates a complete machine-learning workflow starting from raw dataset loading and exploratory analysis through preprocessing, classification, class-imbalance handling, hyperparameter tuning, regression, evaluation, and model persistence.

The final tuned Random Forest pipeline is saved as:

```text
models/best_tuned_random_forest_pipeline.joblib
```

The project can be reproduced by installing the dependencies, running `01_eda.ipynb`, and then running `02_modeling.ipynb`.
