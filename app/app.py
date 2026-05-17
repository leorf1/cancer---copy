# this code is for the main app anf it also allows the users to store and retrieve data from their sqllite database


import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sqlite3
import os
import sys
from PIL import Image

# Add parent directory to path to import model modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Function to create or connect to the SQLite database
def create_connection():
    conn = sqlite3.connect('user_data.db')
    return conn

# Function to create table in the database
def create_table():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_info
                 (id INTEGER PRIMARY KEY, 
                  name TEXT, 
                  diagnosis TEXT, 
                  radius_mean REAL, 
                  texture_mean REAL, 
                  perimeter_mean REAL, 
                  area_mean REAL,
                  smoothness_mean REAL, 
                  compactness_mean REAL, 
                  concavity_mean REAL,
                  concave_points_mean REAL,
                  symmetry_mean REAL,
                  fractal_dimension_mean REAL)''')
    # Create table for image predictions
    c.execute('''CREATE TABLE IF NOT EXISTS image_predictions
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  diagnosis TEXT,
                  probability_benign REAL,
                  probability_malignant REAL,
                  prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Function to store user data in the database
def store_user_data(name, diagnosis, input_data):
    conn = create_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO user_info (name, diagnosis, radius_mean, texture_mean, perimeter_mean, area_mean, 
                 smoothness_mean, compactness_mean, concavity_mean, concave_points_mean, symmetry_mean, 
                 fractal_dimension_mean) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (name, diagnosis,
               input_data['radius_mean'], input_data['texture_mean'], input_data['perimeter_mean'], input_data['area_mean'],
               input_data['smoothness_mean'], input_data['compactness_mean'], input_data['concavity_mean'],
               input_data['concave points_mean'], input_data['symmetry_mean'], input_data['fractal_dimension_mean']))
    conn.commit()
    conn.close()

# Function to retrieve user data from the database
def retrieve_user_data(name):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM user_info WHERE name = ?', (name,))
    data = c.fetchall()
    conn.close()
    return data


def get_clean_data():
    data = pd.read_csv("C:\\Users\\Ali\\Desktop\\Cancer - Copy\\data\\data.csv")
    data = data.drop(['Unnamed: 32', 'id'], axis=1)
    data['diagnosis'] = data['diagnosis'].map({'M': 1, 'B': 0})
    return data


def add_sidebar():
    st.sidebar.header("Cell Nuclei Measurements")
    data = get_clean_data()
    slider_labels = [
        ("Radius (mean)", "radius_mean"),
        ("Texture (mean)", "texture_mean"),
        ("Perimeter (mean)", "perimeter_mean"),
        ("Area (mean)", "area_mean"),
        ("Smoothness (mean)", "smoothness_mean"),
        ("Compactness (mean)", "compactness_mean"),
        ("Concavity (mean)", "concavity_mean"),
        ("Concave points (mean)", "concave points_mean"),
        ("Symmetry (mean)", "symmetry_mean"),
        ("Fractal dimension (mean)", "fractal_dimension_mean"),
        ("Radius (se)", "radius_se"),
        ("Texture (se)", "texture_se"),
        ("Perimeter (se)", "perimeter_se"),
        ("Area (se)", "area_se"),
        ("Smoothness (se)", "smoothness_se"),
        ("Compactness (se)", "compactness_se"),
        ("Concavity (se)", "concavity_se"),
        ("Concave points (se)", "concave points_se"),
        ("Symmetry (se)", "symmetry_se"),
        ("Fractal dimension (se)", "fractal_dimension_se"),
        ("Radius (worst)", "radius_worst"),
        ("Texture (worst)", "texture_worst"),
        ("Perimeter (worst)", "perimeter_worst"),
        ("Area (worst)", "area_worst"),
        ("Smoothness (worst)", "smoothness_worst"),
        ("Compactness (worst)", "compactness_worst"),
        ("Concavity (worst)", "concavity_worst"),
        ("Concave points (worst)", "concave points_worst"),
        ("Symmetry (worst)", "symmetry_worst"),
        ("Fractal dimension (worst)", "fractal_dimension_worst"),
    ]

    input_dict = {}
    for label, key in slider_labels:
        input_dict[key] = st.sidebar.slider(
            label,
            min_value=float(0),
            max_value=float(data[key].max()),
            value=float(data[key].mean())
        )
    return input_dict


def get_scaled_values(input_dict):
    data = get_clean_data()
    X = data.drop(['diagnosis'], axis=1)
    scaled_dict = {}
    for key, value in input_dict.items():
        max_val = X[key].max()
        min_val = X[key].min()
        scaled_value = (value - min_val) / (max_val - min_val)
        scaled_dict[key] = scaled_value
    return scaled_dict


def get_radar_chart(input_data):
    input_data = get_scaled_values(input_data)
    categories = ['Radius', 'Texture', 'Perimeter', 'Area',
                  'Smoothness', 'Compactness',
                  'Concavity', 'Concave Points',
                  'Symmetry', 'Fractal Dimension']

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[input_data['radius_mean'], input_data['texture_mean'], input_data['perimeter_mean'],
           input_data['area_mean'], input_data['smoothness_mean'], input_data['compactness_mean'],
           input_data['concavity_mean'], input_data['concave points_mean'], input_data['symmetry_mean'],
           input_data['fractal_dimension_mean']
           ],
        theta=categories,
        fill='toself',
        name='Mean Value'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[input_data['radius_se'], input_data['texture_se'], input_data['perimeter_se'], input_data['area_se'],
           input_data['smoothness_se'], input_data['compactness_se'], input_data['concavity_se'],
           input_data['concave points_se'], input_data['symmetry_se'], input_data['fractal_dimension_se']
           ],
        theta=categories,
        fill='toself',
        name='Standard Error'
    ))
    fig.add_trace(go.Scatterpolar(
        r=[input_data['radius_worst'], input_data['texture_worst'], input_data['perimeter_worst'],
           input_data['area_worst'], input_data['smoothness_worst'], input_data['compactness_worst'],
           input_data['concavity_worst'], input_data['concave points_worst'], input_data['symmetry_worst'],
           input_data['fractal_dimension_worst']
           ],
        theta=categories,
        fill='toself',
        name='Worst Value'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=11)
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1
        ),
        height=500,
        margin=dict(l=50, r=150, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def add_predictions(input_data):
    model = pickle.load(open("C:\\Users\\Ali\\Desktop\\Cancer - Copy\\model\\model.pkl", "rb"))
    scaler = pickle.load(open("C:\\Users\\Ali\\Desktop\\Cancer - Copy\\model\\scaler.pkl", "rb"))

    input_array = np.array(list(input_data.values())).reshape(1, -1)

    input_array_scaled = scaler.transform(input_array)

    prediction = model.predict(input_array_scaled)
    probabilities = model.predict_proba(input_array_scaled)[0]

    st.markdown("### 🔬 Cell Cluster Prediction")
    st.markdown("---")
    
    # Display prediction with enhanced styling
    if prediction[0] == 0:
        st.markdown('<div class="diagnosis-benign">✓ BENIGN</div>', unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown('<div class="diagnosis-malignant">⚠ MALIGNANT</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display probabilities with metrics
    col1, col2 = st.columns(2)
    
    with col1:
        prob_benign = probabilities[0]
        st.metric(
            label="🟢 Benign Probability",
            value=f"{prob_benign:.2%}",
            delta=f"{prob_benign*100:.1f}%"
        )
        st.progress(prob_benign)
    
    with col2:
        prob_malignant = probabilities[1]
        st.metric(
            label="🔴 Malignant Probability",
            value=f"{prob_malignant:.2%}",
            delta=f"{prob_malignant*100:.1f}%"
        )
        st.progress(prob_malignant)

    return prediction[0]

def predict_from_image(uploaded_file):
    """
    Predict benign or malignant from an uploaded image.
    """
    if not IMAGE_MODEL_AVAILABLE:
        st.error("❌ Image prediction is not available. Please install TensorFlow: `pip install tensorflow`")
        return None, None, None, None
    
    try:
        # Load image model
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model', 'image_model.keras')
        
        if not os.path.exists(model_path):
            st.error(f"❌ Model file not found at {model_path}. Please train the model first using model/train_image_model.py")
            return None, None, None, None
        
        image_model = load_image_model(model_path)
        
        # Load and process image
        img = Image.open(uploaded_file)
        
        # Make prediction
        prediction, prob_benign, prob_malignant = predict_image(image_model, img)
        
        return prediction, prob_benign, prob_malignant, img
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None, None, None


def main():
    create_table()  # Create the table if it doesn't exist

    st.set_page_config(
        page_title="Breast Cancer Predictor",
        page_icon=":female-doctor:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add navigation tabs
    tab1, tab2 = st.tabs(["📊 Feature-Based Prediction", "🖼️ Image-Based Prediction"])

    with tab1:
        input_data = add_sidebar()

        # Header section
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>🔬 Breast Cancer Predictor</h1>
            <p style='color: white; font-size: 1.1rem; margin-top: 0.5rem;'>
                AI-Powered Diagnosis Based on Cell Nuclei Measurements
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **How it works:** Adjust the cell measurements using the sliders in the sidebar. The model will analyze the features and predict whether the tumor is benign or malignant.")

        # Create a container for the radar chart and prediction
        col1, col2 = st.columns([2, 1])  # Two columns, one for the chart and one for the prediction

        with col1:
            # Radar chart at the top
            st.markdown("### 📊 Cell Feature Visualization")
            radar_chart = get_radar_chart(input_data)
            st.plotly_chart(radar_chart, use_container_width=True)

        with col2:
            # Cell Cluster Prediction on the right
            diagnosis = add_predictions(input_data)
            
            st.markdown("---")
            
            # Create the form on the right (beneath the prediction)
            with st.expander("💾 Save Prediction", expanded=False):
                with st.form("user_form"):
                    name = st.text_input("👤 Name", placeholder="Enter your name")
                    user_id = st.text_input("🆔 ID Number", placeholder="Enter ID number")
                    submit_button = st.form_submit_button(label="💾 Save to Database", use_container_width=True)

                if submit_button:
                    if name:
                        # Get predictions
                        diagnosis = add_predictions(input_data)

                        # Store the data in the database
                        store_user_data(name, "Malignant" if diagnosis == 1 else "Benign", input_data)

                        st.success(f"✅ **Success!** Prediction saved for {name}.")
                    else:
                        st.warning("⚠️ Please enter your name to save the prediction.")

        # Search section
        st.markdown("---")
        st.markdown("### 🔍 Retrieve Saved Predictions")
        search_name = st.text_input("Enter your name to retrieve your data:", placeholder="Type your name here...", key="search_feature")
        if search_name:
            user_data = retrieve_user_data(search_name)
            if user_data:
                st.success(f"Found {len(user_data)} record(s) for {search_name}")
                for idx, data in enumerate(user_data, 1):
                    with st.expander(f"📋 Record #{idx} - {data[2]}", expanded=False):
                        st.json({
                            "ID": data[0],
                            "Name": data[1],
                            "Diagnosis": data[2],
                            "Radius Mean": f"{data[3]:.2f}",
                            "Texture Mean": f"{data[4]:.2f}",
                            "Perimeter Mean": f"{data[5]:.2f}",
                            "Area Mean": f"{data[6]:.2f}",
                            "Smoothness Mean": f"{data[7]:.4f}",
                            "Compactness Mean": f"{data[8]:.4f}",
                            "Concavity Mean": f"{data[9]:.4f}",
                            "Concave Points Mean": f"{data[10]:.4f}",
                            "Symmetry Mean": f"{data[11]:.4f}",
                            "Fractal Dimension Mean": f"{data[12]:.4f}"
                        })
            else:
                st.warning(f"❌ No data found for '{search_name}'. Please check the name and try again.")

    with tab2:
        # Header section
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0;'>🖼️ Image-Based Classification</h1>
            <p style='color: white; font-size: 1.1rem; margin-top: 0.5rem;'>
                AI-Powered Diagnosis from Cell Images
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Note:** This feature is currently under development. Image prediction functionality will be available soon.")
        
        # Image upload section
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            help="Upload a cell image (PNG, JPG, JPEG, BMP, or TIFF format)",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            st.markdown("### 📷 Uploaded Image")
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Cell Image", use_container_width=True)
            
            st.info("🔄 Image processing and prediction functionality will be implemented here.")

if __name__ == '__main__':
    main()
