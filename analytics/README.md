\# Module 2 — Analytics Pipeline



\## Overview



This module implements an end-to-end Titanic analytics and predictive modeling pipeline.



The workflow covers:



1\. Dataset loading and profiling

2\. Missing-value handling

3\. Exploratory Data Analysis (EDA)

4\. Univariate, bivariate, and multivariate analysis

5\. EDA standardization sanity check

6\. Classification modeling

7\. Class-imbalance analysis

8\. Random Forest hyperparameter tuning

9\. Multivariate linear regression for fare prediction

10\. Final model comparison

11\. Saving and reloading the complete trained pipeline



The raw Titanic dataset is loaded through Seaborn once in `01\_eda.ipynb`. The exact loaded dataset is saved as `titanic.csv` and reused by `02\_modeling.ipynb`.







\## Project Structure



```text

analytics/

├── 01\_eda.ipynb

├── 02\_modeling.ipynb

├── titanic.csv

├── requirements.txt

├── README.md

│

├── models/

│   └── best\_tuned\_random\_forest\_pipeline.joblib

│

└── outputs/

&#x20;   ├── multivariate\_01\_survival\_sex\_class.png

&#x20;   ├── multivariate\_02\_age\_fare\_survival.png

&#x20;   ├── multivariate\_03\_fare\_class\_survival.png

&#x20;   ├── multivariate\_04\_sibsp\_class\_survival.png

&#x20;   └── regression\_residual\_plot.png



\## Dataset Loading and Profiling



\# Part A — Profiling, Cleaning and EDA



\## 1. Dataset Loading and Profiling



The classic Titanic dataset was loaded using:



```python

sns.load\_dataset("titanic")



The loaded dataset contains:



Rows: 891

Columns: 15



The exact loaded DataFrame was immediately saved as:



df.to\_csv("titanic.csv", index=False)

This CSV provides an offline fallback for the modeling notebook.



The modeling stage reads this committed CSV instead of independently loading the Titanic dataset again from the network.





\## 2. Missing-Value Analysis



The following columns contained missing values:



| Column | Missing Count | Missing Percentage | Strategy |

|---|---:|---:|---|

| `age` | 177 | 19.87% | Median imputation |

| `embarked` | 2 | 0.22% | Drop affected rows |

| `deck` | 688 | 77.22% | Drop column |

| `embark\_town` | 2 | 0.22% | Drop affected rows |



The threshold rule was:



\- Less than 5% missing → drop affected rows

\- 5%–30% missing → impute

\- Very high missingness → drop the column when reliable imputation is not appropriate. The `deck` column had 77.22% missing values, so it was dropped because this level of missingness makes reliable imputation inappropriate.

After cleaning, the dataset contained \*\*889 rows and 14 columns\*\*.



\## 3. Univariate Analysis



\### Age



\- Q1 = 22.0

\- Q3 = 35.0

\- IQR = 13.0

\- Outliers = \*\*65\*\*



The age distribution is concentrated mainly between 20 and 40 years.



\### Fare



\- Mean = 32.0967

\- Median = 14.4542

\- Mode = 8.05

\- IQR outliers = \*\*114\*\*



Since \*\*Mean > Median > Mode\*\*, the fare distribution is \*\*right-skewed\*\*. The histogram and box plot also show a smaller number of unusually high fares.



\## 4. Bivariate Analysis



\### Survival Rate



| Group | Survival Rate |

|---|---:|

| Female | 74.04% |

| Male | 18.89% |

| 1st Class | 62.62% |

| 2nd Class | 47.28% |

| 3rd Class | 24.24% |



By sex and passenger class:



\- Female, 1st class: \*\*96.74%\*\*

\- Female, 2nd class: \*\*92.11%\*\*

\- Female, 3rd class: \*\*50.00%\*\*

\- Male, 1st class: \*\*36.89%\*\*

\- Male, 2nd class: \*\*15.74%\*\*

\- Male, 3rd class: \*\*13.54%\*\*



Boolean masking with `\&` and `|` was also used for combined conditions.



\### Correlation



The correlation matrix used exactly:



`survived`, `pclass`, `age`, `sibsp`, `parch`, `fare`



The two strongest absolute correlations were:



\- `pclass` and `fare`: \*\*-0.5482\*\*

\- `sibsp` and `parch`: \*\*0.4145\*\*



The columns `adult\_male` and `alone` were excluded because they are derived/redundant flags.



## 5. Multivariate Data Story

Four charts were created to examine survival using multiple passenger characteristics.

1. **Survival by Sex and Class** — Survival varies by both sex and passenger class. Female passengers generally had higher survival rates than male passengers within the same class, while higher-class passengers also showed higher survival in several groups.

2. **Age, Fare and Survival** — Fare is concentrated at lower values, while some passengers paid much higher fares. Survival varies across different age and fare combinations, showing that age or fare alone does not fully explain the observed outcomes.

3. **Fare by Class and Survival** — Higher passenger classes generally have higher fares, with several high-fare outliers. Survival also varies within each class, indicating that passenger class and fare are related to the observed survival patterns.

4. **Survival by Siblings/Spouses and Class** — Survival patterns vary with the number of siblings or spouses and passenger class. Passenger class continues to distinguish survival patterns across different family-group sizes, showing the value of considering multiple characteristics together.



\## 6. EDA Standardization Sanity Check



Age and fare were standardized using z-score standardization.



| Feature | Before Mean | Before Std |

|---|---:|---:|

| Age | 29.3152 | 12.9849 |

| Fare | 32.0967 | 49.6975 |



After standardization, both features had means approximately \*\*0\*\* and standard deviations approximately \*\*1\*\*.



This confirms that the standardization worked correctly. This step was used only for EDA validation and was not used directly in the modeling pipeline.



\# Part B — Predictive Modeling



\## 7. Classification Setup



The target variable was `survived`.



Features used:



`pclass`, `sex`, `age`, `sibsp`, `parch`, `fare`, `embarked`



The data was split using an 80/20 stratified train/test split.



\- Training samples: \*\*711\*\*

\- Testing samples: \*\*178\*\*

\- Not Survived: \*\*61.75%\*\*

\- Survived: \*\*38.25%\*\*



Stratification was used to preserve the class distribution in both sets.



\## 8. Preprocessing



A `ColumnTransformer` and `Pipeline` were used.



\- Numeric features: median imputation + `StandardScaler`

\- Categorical features: most-frequent imputation + one-hot encoding

\- Preprocessing was fitted on training data and then applied to the test data.



\## 9. Classification Models



Three classifiers were trained on the same split:



\- Logistic Regression

\- Decision Tree

\- Random Forest



The Decision Tree was visualized using `plot\_tree` with feature and class names.







\## 10. Classification Results



| Model | Accuracy | Precision | Recall | F1 | AUC |

|---|---:|---:|---:|---:|---:|

| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |

| Decision Tree | 0.7697 | 0.6901 | 0.7206 | 0.7050 | 0.7541 |

| Random Forest | 0.8202 | 0.7812 | 0.7353 | 0.7576 | 0.8179 |

| Tuned Random Forest | 0.8315 | 0.8654 | 0.6618 | 0.7500 | 0.8389 |



Confusion matrices and ROC curves with AUC were generated for the three original classifiers.



\## 11. Class Imbalance Experiment



Three Logistic Regression approaches were compared:



| Strategy | Precision | Recall | F1 |

|---|---:|---:|---:|

| Baseline | 0.7833 | 0.6912 | 0.7344 |

| Class Weight = Balanced | 0.7183 | 0.7500 | 0.7338 |

| SMOTE | 0.7353 | 0.7353 | 0.7353 |



The baseline produced the highest precision, class weighting produced the highest recall, and SMOTE produced the highest F1-score.



The F1 differences were small, while SMOTE provided the most balanced precision-recall result in this experiment. SMOTE was applied only to the training data to avoid test-set leakage.





\## 12. Random Forest Hyperparameter Tuning



GridSearchCV was used to tune `n\_estimators`, `max\_depth`, and `max\_features`.



Best parameters:



\- `n\_estimators` = \*\*200\*\*

\- `max\_depth` = \*\*5\*\*

\- `max\_features` = \*\*sqrt\*\*



Best cross-validation F1-score: \*\*0.7408\*\*



OOB score: \*\*0.8214\*\*



The tuned Random Forest achieved the following test-set results:



| Metric | Value |

|---|---:|

| Accuracy | 0.8315 |

| Precision | 0.8654 |

| Recall | 0.6618 |

| F1 | 0.7500 |

| AUC | 0.8389 |



\## 13. Regression Side-Task



A multivariate Linear Regression model was used to predict `fare` from the available passenger features.



| Metric | Value |

|---|---:|

| MAE | 18.3945 |

| RMSE | 41.3578 |

| R² | 0.3589 |

| Adjusted R² | 0.2679 |



The residual plot shows that the spread of residuals increases as predicted fare increases. Therefore, the model shows evidence of \*\*heteroscedasticity\*\*, meaning the residual variance is not constant.



\## 14. Final Comparison and Deployment Recommendation



\### Classification



| Model | Accuracy | Precision | Recall | F1 | AUC |

|---|---:|---:|---:|---:|---:|

| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |

| Decision Tree | 0.7697 | 0.6901 | 0.7206 | 0.7050 | 0.7541 |

| Random Forest | 0.8202 | 0.7812 | 0.7353 | 0.7576 | 0.8179 |

| Tuned Random Forest | 0.8315 | 0.8654 | 0.6618 | 0.7500 | 0.8389 |



\### Regression



| MAE | RMSE | R² | Adjusted R² |

|---:|---:|---:|---:|

| 18.3945 | 41.3578 | 0.3589 | 0.2679 |



Classification and regression metrics are presented separately because they measure different types of predictive performance.



\### Deployment Recommendation



The tuned Random Forest achieved the highest test accuracy (0.8315) and precision (0.8654), with an F1-score of 0.7500. Logistic Regression achieved the highest AUC (0.8610), while the tuned Random Forest had a lower recall of 0.6618. The Decision Tree achieved an accuracy of 0.7697 and AUC of 0.7541. Based on the test-set accuracy, precision, and F1-score, the tuned Random Forest was selected as the deployment model, while the differences in AUC and recall were also considered.





\## 15. Saved Model and Reproducibility



The complete tuned Random Forest pipeline, including preprocessing and the trained estimator, was saved using `joblib`.



Saved model:



```text

models/best\_tuned\_random\_forest\_pipeline.joblib



\## 16. How to Run



From the project root:



```powershell

cd analytics



Activate the virtual environment:

..\\.venv\\Scripts\\Activate.ps1



Install dependencies:

pip install -r requirements.txt



Start Jupyter: 

jupyter notebook



Run the notebooks in this order:



01\_eda.ipynb

02\_modeling.ipynb



01\_eda.ipynb creates titanic.csv and the EDA output charts.



02\_modeling.ipynb reads titanic.csv, trains and evaluates the models, performs tuning and regression, and saves the final pipeline to models/.





\## 17. Dependencies and Outputs



The required Python packages are listed in `requirements.txt`.



The main generated artifacts are:



\- `titanic.csv` — offline copy of the source dataset

\- `outputs/` — EDA and regression visualizations

\- `models/best\_tuned\_random\_forest\_pipeline.joblib` — saved deployment pipeline



The notebooks contain the detailed analysis, interpretations, model evaluation, and conclusions.

## Verification

The analytics pipeline was verified after execution. The notebooks, committed Titanic dataset, generated visualizations, trained model pipeline, requirements file, and documentation are included in this module.