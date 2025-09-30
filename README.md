


# ⚽ ProFootball Injury Risk AI

## 📌 Project Overview

Football clubs face huge financial and sporting losses when key players get injured. Preventing injuries requires **early detection of risk factors** such as training load, match frequency, recovery, and fitness.

This project builds a **Machine Learning (ML) system using boosting algorithms** (XGBoost, Gradient Boosting, AdaBoost) to predict injury risk for football players.

The project also provides an **interactive Streamlit web app** that allows coaches, analysts, or sports scientists to:

* Input player data
* Get an **injury risk probability**
* See **SHAP explainability** (which factors contributed most)
* Track **historical trends**
* View **recommendations for injury prevention**

---

## 🎯 Objectives

1. Predict whether a football player is at risk of injury in the next match/training.
2. Provide **transparent model explanations** using SHAP.
3. Deploy a **user-friendly AI dashboard** for coaches & analysts.

---

## 📊 Dataset & Features

We combined multiple football-related datasets:

* **FIFA Player Attributes** – skills & fitness stats
* **Match Logs** – minutes played, matches per week, substitutions
* **Injury Records** – historical injury events
* **Synthetic Features** – engineered from available data

### Example Features

| Feature           | Description                               |
| ----------------- | ----------------------------------------- |
| Age               | Player’s age                              |
| Position          | Forward, Midfielder, Defender, Goalkeeper |
| Minutes played    | Total minutes in past match/week/month    |
| Match frequency   | Matches per week                          |
| Training load     | Hours × intensity factor                  |
| Previous injuries | Count of major injuries                   |
| Recovery time     | Days since last match/training            |
| Fitness rating    | FIFA-style overall rating                 |
| BMI               | Player’s body mass index                  |

### Target Variable

* **Binary Classification**

  * `1 = High Injury Risk`
  * `0 = Safe`
* (Optional) Multi-class: Minor / Moderate / Severe injury

---

## 🧠 Why Boosting Algorithms?

Boosting methods are well-suited for **tabular sports datasets**:

* ✅ Handle missing values gracefully
* ✅ Capture **complex, nonlinear interactions** (fatigue × match load × age)
* ✅ Provide **feature importance** for interpretability
* ✅ High accuracy compared to logistic regression or simple models

---

## 🛠️ Methodology

### 1. Data Preprocessing

* Handle missing values (mean/median imputation)
* Encode categorical features (e.g., Position → one-hot encoding)
* Normalize continuous features (age, BMI, load)

### 2. Feature Engineering

* Rolling averages for fatigue/load
* Interaction features (e.g., Age × Minutes Played)
* Fatigue Index = weighted sum of training + matches

### 3. Modeling

Trained three ML classifiers:

* **XGBoost**
* **Gradient Boosting**
* **AdaBoost**

### 4. Evaluation

Metrics used:

* Accuracy
* F1-score
* ROC-AUC
* Confusion Matrix

---

## 📈 Results

### 🔹 XGBoost

* Accuracy: **79.7%**
* F1 Score: **0.855**
* ROC-AUC: **0.748**

Confusion Matrix:

```
[[ 52  34]
 [ 19 156]]
```

---

### 🔹 Gradient Boosting

* Accuracy: **79.7%**
* F1 Score: **0.853**
* ROC-AUC: **0.754**

Confusion Matrix:

```
[[ 54  32]
 [ 21 154]]
```

---

### 🔹 AdaBoost

* Accuracy: **80.5%**
* F1 Score: **0.868**
* ROC-AUC: **0.727**

Confusion Matrix:

```
[[ 43  43]
 [  8 167]]
```

✅ **Best Model**: **AdaBoost** achieved the **highest accuracy & F1 score**, though XGBoost provided better interpretability.

---

## 🚀 Streamlit Web App

### Features

* 🎨 **Modern UI** with custom CSS & animations
* 📊 **Risk Prediction Dashboard**
* 🧠 **Explainable AI (SHAP)** visualization
* ⏳ **Historical trend tracking**
* 💡 **Personalized recommendations**
* 📰 **Latest player news (simulated)**

### Usage

1. Run the app:

   ```bash
   streamlit run main.py
   ```
2. Enter player details in the sidebar:

   * Age, BMI, FIFA rating, minutes played, etc.
3. Click **🔮 Predict Injury Risk**
4. View results across 5 tabs:

   * **Summary** → Risk level & probability
   * **Model Insights** → SHAP + radar chart
   * **Historical Trends** → Probability timeline
   * **Recommendations** → Tailored advice
   * **Raw Data & Debug** → Input vs scaled data

---

## 📂 Project Structure

```
📁 ProFootball-Injury-Risk
 ┣ 📜 main.py              # Streamlit web app
 ┣ 📜 football_injury_model.pkl   # Trained ML model
 ┣ 📜 scaler.pkl           # Data scaler
 ┣ 📜 README.md            # Project documentation
 ┣ 📂 data/                # Raw & processed datasets
 ┣ 📂 notebooks/           # Jupyter notebooks for training
 ┗ 📂 reports/             # Visualizations, results
```

---

## 🔮 Future Work

* Integrate **real player GPS & wearable sensor data**
* Deploy as a **club-level monitoring system**
* Extend to other sports (basketball, cricket, rugby)
* Use **time-series models (LSTM/Transformers)** for fatigue trends
* Add **severity classification** (minor/moderate/severe injury)

---

## 🙌 Acknowledgements

* Open-source FIFA datasets
* Research on sports injury prediction
* SHAP library for explainability
* Streamlit for deployment
