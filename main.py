import streamlit as st
import pandas as pd
import joblib
import streamlit.components.v1 as components
import plotly.graph_objects as go
import shap
import time
from datetime import datetime
import numpy as np

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="ProFootball Injury Risk AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Initialize Session State for History
# -----------------------------
if 'history' not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Custom JavaScript Animation Component
# -----------------------------
def football_animation_component():
    """Returns an HTML component with a self-contained JS football animation."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { margin: 0; overflow: hidden; background-color: transparent; }
        canvas { 
            display: block; 
            border-radius: 12px;
        }
    </style>
    </head>
    <body>
    <canvas id="footballAnimation"></canvas>
    <script>
        const canvas = document.getElementById('footballAnimation');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            let parent = canvas.parentElement;
            canvas.width = parent.clientWidth;
            canvas.height = 400; 
        }
        
        resizeCanvas();

        const groundLevel = canvas.height - 40;

        let ball = {
            x: 85, y: groundLevel - 12, radius: 10, dx: 0, dy: 0,
            gravity: 0.3, rotation: 0, isKicked: false
        };

        let player = {
            x: 50, y: groundLevel, width: 20, height: 50,
            speed: 1.5, runFrame: 0, isKicking: false
        };

        function drawField() {
            ctx.fillStyle = '#228B22'; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#87CEEB'; 
            ctx.fillRect(0, 0, canvas.width, groundLevel - 20);
            ctx.fillStyle = '#228B22';
            ctx.fillRect(0, groundLevel - 20, canvas.width, canvas.height - 20);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2, groundLevel - 20);
            ctx.lineTo(canvas.width / 2, canvas.height);
            ctx.stroke();
        }

        function drawPlayer() {
            const p = player;
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(p.x, p.y - p.height, 8, 0, Math.PI * 2);
            ctx.fillStyle = '#FFFFFF';
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(p.x, p.y - p.height + 8);
            ctx.lineTo(p.x, p.y - 15);
            ctx.stroke();
            if (p.isKicking) {
                ctx.beginPath();
                ctx.moveTo(p.x, p.y - 15);
                ctx.lineTo(p.x + 15, p.y - 10);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(p.x, p.y - 15);
                ctx.lineTo(p.x - 10, p.y - 2);
                ctx.stroke();
            } else { 
                let legAngle = Math.sin(p.runFrame * 0.3) * 0.6;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y - 15);
                ctx.lineTo(p.x + Math.sin(legAngle) * 15, p.y - 2);
                ctx.moveTo(p.x, p.y - 15);
                ctx.lineTo(p.x + Math.sin(legAngle + Math.PI) * 15, p.y - 2);
                ctx.stroke();
            }
        }
        
        function updatePlayerAndBall() {
            player.x += player.speed;
            player.runFrame += 1;
            if (player.x > ball.x - 30 && !ball.isKicked) {
                player.isKicking = true;
                ball.isKicked = true;
                ball.dx = 6;
                ball.dy = -6;
            } else {
                player.isKicking = false;
            }
            if (ball.isKicked) {
                ball.dy += ball.gravity;
                ball.x += ball.dx;
                ball.y += ball.dy;
                ball.rotation += ball.dx * 0.1;
                if (ball.y + ball.radius > groundLevel) {
                    ball.y = groundLevel - ball.radius;
                    ball.dy *= -0.6;
                    ball.dx *= 0.8;
                }
            } else {
               ball.x = player.x + 35;
               ball.y = groundLevel - ball.radius;
            }
            if (player.x > canvas.width + player.width) {
                player.x = -player.width;
                ball.isKicked = false;
            }
        }

        function drawBall() {
            ctx.save();
            ctx.translate(ball.x, ball.y);
            ctx.rotate(ball.rotation);
            ctx.beginPath();
            ctx.arc(0, 0, ball.radius, 0, Math.PI * 2);
            ctx.fillStyle = '#FFFFFF';
            ctx.fill();
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1;
            ctx.moveTo(ball.radius, 0);
            for (let i = 1; i <= 6; i++) {
                ctx.lineTo(ball.radius * Math.cos(i * 2 * Math.PI / 6), ball.radius * Math.sin(i * 2 * Math.PI / 6));
            }
            ctx.stroke();
            ctx.closePath();
            ctx.restore();
        }

        function animate() {
            requestAnimationFrame(animate);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawField();
            updatePlayerAndBall();
            drawPlayer();
            drawBall();
        }
        
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                resizeCanvas();
                player.x = 50;
                ball.isKicked = false;
            }, 100);
        });

        animate();
    </script>
    </body>
    </html>
    """
    return components.html(html_code, height=400)


# -----------------------------
# Custom CSS for Advanced Styling
# -----------------------------
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(to right top, #0f172a, #1e293b, #334155);
            font-family: 'Poppins', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        .stSelectbox div[data-baseweb="select"] > div {
            color: #000000 !important;
            font-weight: 700 !important;
        }
        
        .stTitle {
            font-size: 3.5em !important; color: #E2E8F0 !important; font-weight: 700 !important;
        }
        .stMarkdown p {
             font-size: 1.1rem !important; color: #cdd6e3 !important; font-weight: 400 !important;
        }
        [data-testid="stSidebar"] { 
            background-color: #1E293B; border-right: 1px solid #334155; 
        }
        .stButton>button {
            border-radius: 12px; border: 2px solid #38BDF8; color: #38BDF8 !important;
            background-color: transparent; font-weight: 600 !important;
            padding: 12px 28px; width: 100%; font-size: 1.1em;
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #38BDF8; color: #0F172A !important; transform: scale(1.05);
            box-shadow: 0px 5px 15px rgba(56, 189, 248, 0.4);
        }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border-radius: 8px; color: #94A3B8; font-weight: 600 !important; }
        .stTabs [data-baseweb="tab--selected"] { background-color: #334155; color: #E2E8F0 !important; }
        
        [data-testid="stMetric"] { background-color: #1E293B; padding: 20px; border-radius: 12px; }
        
        iframe { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

load_css()

# -----------------------------
# Load Model, Scaler, and SHAP Explainer
# -----------------------------
@st.cache_resource
def load_resources():
    try:
        model = joblib.load("football_injury_model.pkl")
        scaler = joblib.load("scaler.pkl")
        explainer = shap.TreeExplainer(model)
        return model, scaler, explainer
    except FileNotFoundError:
        st.error("Model or scaler file not found. Please ensure 'football_injury_model.pkl' and 'scaler.pkl' are in the same directory as your script.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred loading the resources: {e}")
        st.stop()


model, scaler, explainer = load_resources()
expected_features = scaler.feature_names_in_

# -----------------------------
# Helper Functions
# -----------------------------
def format_label(feature_name):
    return feature_name.replace('_', ' ').title()

def create_radar_chart(df):
    radar_features = ['age', 'bmi', 'fifa_rating']
    radar_features = [f for f in radar_features if f in df.columns]
    if not radar_features: return go.Figure()

    ranges = {'age': (15, 45), 'bmi': (15, 40), 'fifa_rating': (40, 100)}
    values = [100 * (df[f].iloc[0] - ranges[f][0]) / (ranges[f][1] - ranges[f][0]) for f in radar_features]

    fig = go.Figure(data=go.Scatterpolar(r=values, theta=[format_label(f) for f in radar_features], fill='toself', marker_color='#38BDF8', line_color='#38BDF8'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, ticks=''), angularaxis=dict(tickfont=dict(size=12, color='white'))), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
    return fig

def get_recommendations(user_data, non_model_data, prediction_proba):
    recs = []
    if prediction_proba > 0.75: recs.append("🔴 **Immediate Action:** High-risk probability. Strongly consider resting the player.")
    elif prediction_proba > 0.5: recs.append("🟠 **High Alert:** Player is at high risk. Implement a personalized pre-hab routine and monitor training load.")
    if user_data['age'].iloc[0] > 32: recs.append("Age Factor: Focus on dynamic stretching and post-session recovery.")
    if user_data['bmi'].iloc[0] > 25: recs.append("BMI Factor: Consider a nutritional consultation to optimize body composition.")
    if 'total_minutes_played' in user_data and user_data['total_minutes_played'].iloc[0] > 2500: recs.append("Workload Factor: High accumulated fatigue. Prioritize recovery sessions.")
    if non_model_data['previous_injuries'] > 0: recs.append(f"Injury History: With {non_model_data['previous_injuries']} prior injuries, strengthen those areas.")
    if not recs: recs.append("✅ **Low Risk:** Player is in good physical condition. Continue standard monitoring.")
    return recs

def create_history_chart():
    if not st.session_state.history: return go.Figure().update_layout(title="No historical data yet.", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#1E293B', font_color='white')
    
    hist_df = pd.DataFrame(st.session_state.history)
    fig = go.Figure(go.Scatter(x=hist_df['timestamp'], y=hist_df['probability'], mode='lines+markers', marker_color='#38BDF8', line_color='#38BDF8'))
    fig.update_layout(title="Player Injury Risk Over Time", xaxis_title="Date", yaxis_title="Injury Probability", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#1E293B', font_color='white', yaxis=dict(range=[0,1]))
    return fig

# ========== FIXED FUNCTION HERE ==========
@st.cache_data
def get_shap_html(_input_df_for_cache):
    """Computes SHAP values and returns an HTML representation for Streamlit."""
    input_scaled = scaler.transform(_input_df_for_cache)
    shap_values = explainer.shap_values(input_scaled)
    
    # Robustly handle different output formats of shap_values and expected_value
    if isinstance(shap_values, list) and len(shap_values) > 1:
        # Typical case for binary classifiers: list of two arrays
        shap_values_for_plot = shap_values[1] 
        expected_value_for_plot = explainer.expected_value[1]
    else:
        # Case for single output (regressors or some classifiers)
        shap_values_for_plot = shap_values
        expected_value_for_plot = explainer.expected_value

    # Ensure we pass a 1D array to the force_plot
    if hasattr(shap_values_for_plot, 'ndim') and shap_values_for_plot.ndim > 1:
        shap_values_row = shap_values_for_plot[0, :]
    else:
        shap_values_row = shap_values_for_plot

    p = shap.force_plot(
        expected_value_for_plot, 
        shap_values_row, 
        _input_df_for_cache.iloc[0,:], 
        feature_names=expected_features, 
        show=False
    )
    shap_html = f"<head>{shap.getjs()}</head><body>{p.html()}</body>"
    return shap_html
# =======================================

def get_latest_news(player_name):
    if not player_name: return ["Enter a player name to get news."]
    return [
        f"Sources say {player_name} completed a full training session yesterday.",
        "Manager praises player's work ethic in recent press conference.",
        f"Speculation about a minor knock for {player_name} dismissed by the club."
    ]

# -----------------------------
# Sidebar for User Inputs
# -----------------------------
with st.sidebar:
    st.header("👤 Player Identity")
    player_name = st.text_input("Player Name", placeholder="e.g., John Doe")
    
    st.header("📊 Player Attributes")
    user_input = {}
    non_model_input = {}
    non_model_input['position'] = st.selectbox("⚽ Position", ["Forward", "Midfielder", "Defender", "Goalkeeper"])
    non_model_input['previous_injuries'] = st.number_input("🩹 Previous Major Injuries", min_value=0, value=0, step=1)
    
    for feature in expected_features:
        label = format_label(feature)
        if feature.lower() == "age": user_input[feature] = st.slider(f"👤 {label}", 15, 45, 25)
        elif feature.lower() == "bmi": user_input[feature] = st.slider(f"⚖️ {label}", 15.0, 40.0, 22.5, 0.1)
        elif feature.lower() == "fifa_rating": user_input[feature] = st.slider(f"⭐ {label}", 40, 100, 75)
        elif "minutes" in feature.lower(): user_input[feature] = st.number_input(f"⏱️ {label}", min_value=0, value=1500, step=50)
        else: user_input[feature] = st.number_input(f"📈 {label}", value=0.0, format="%.2f")
    
    predict_button = st.button("🔮 Predict Injury Risk")

# -----------------------------
# Main App Interface
# -----------------------------
main_col1, main_col2 = st.columns([1, 1.2])

with main_col1:
    football_animation_component()
    st.markdown('<h1 class="stTitle">ProFootball Risk AI</h1>', unsafe_allow_html=True)
    st.markdown("<p>This tool uses an XGBoost model and SHAP explainability to provide a transparent injury risk assessment. Input player data to generate a detailed report.</p>", unsafe_allow_html=True)
    
    st.subheader("📰 Latest Player News (Simulated)")
    news_items = get_latest_news(player_name)
    for item in news_items:
        st.info(item)

with main_col2:
    if predict_button:
        with st.spinner('Analyzing data and generating report...'):
            time.sleep(1.5)
            try:
                input_df = pd.DataFrame([user_input])[expected_features]
                input_scaled = scaler.transform(input_df)
                prediction_proba = model.predict_proba(input_scaled)[0][1]
                prediction = (prediction_proba > 0.5).astype(int)

                st.subheader(f"Risk Analysis for: {player_name if player_name else 'Unnamed Player'}")
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Summary", "🧠 Model Insights", "📈 Historical Trends", "💡 Recommendations", "⚙️ Raw Data & Debug"])

                with tab1:
                    col1, col2 = st.columns(2)
                    risk_level = "High" if prediction == 1 else "Low"
                    col1.metric(label="Predicted Risk Level", value=risk_level)
                    col2.metric(label="Injury Probability", value=f"{prediction_proba:.1%}")
                    st.progress(float(prediction_proba))
                    if st.button("💾 Save Prediction to History"):
                        st.session_state.history.append({'player_name': player_name, 'probability': prediction_proba, 'timestamp': datetime.now()})
                        st.success(f"Prediction for {player_name} saved!")

                with tab2:
                    st.subheader("Model Prediction Breakdown (SHAP)")
                    st.info("This chart shows which features pushed the prediction higher (red) or lower (blue). Longer bars have a greater impact.")
                    shap_html = get_shap_html(input_df)
                    components.html(shap_html, height=200)
                    st.subheader("Player Attribute Profile")
                    st.plotly_chart(create_radar_chart(input_df), use_container_width=True)

                with tab3:
                    st.subheader("Historical Risk Tracking")
                    st.plotly_chart(create_history_chart(), use_container_width=True)

                with tab4:
                    st.subheader("Tailored Recommendations")
                    recommendations = get_recommendations(input_df, non_model_input, prediction_proba)
                    for rec in recommendations: st.markdown(f"- {rec}")

                with tab5:
                    st.subheader("Raw Input Data (Before Scaling)")
                    st.dataframe(input_df.T.rename(columns={0: 'Value'}), use_container_width=True)
                    
                    st.subheader("Scaled Input Data (Sent to Model)")
                    scaled_df = pd.DataFrame(input_scaled, columns=expected_features)
                    st.dataframe(scaled_df.T.rename(columns={0: 'Value'}), use_container_width=True)
                    st.warning("""
                    **DEBUGGING:** Check if the 'Scaled Input Data' values change when you alter inputs. If they do but the probability doesn't, the issue is likely your model file.
                    """)

            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")
    else:
        st.info("Fill in the player's data on the left and click 'Predict' to see the full analysis dashboard.")
