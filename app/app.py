# this code is for the main app anf it also allows the users to store and retrieve data from their sqllite database


import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import sqlite3

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
    data = pd.read_csv("data/data.csv")
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
                range=[0, 1]
            )),
        showlegend=True
    )

    return fig


def add_predictions(input_data):
    model = pickle.load(open("model/model.pkl", "rb"))
    scaler = pickle.load(open("model/scaler.pkl", "rb"))

    input_array = np.array(list(input_data.values())).reshape(1, -1)

    input_array_scaled = scaler.transform(input_array)

    prediction = model.predict(input_array_scaled)

    st.subheader("Cell cluster prediction")
    st.write("The cell cluster is:")

    if prediction[0] == 0:
        st.write("<span class='diagnosis benign'>Benign</span>", unsafe_allow_html=True)
    else:
        st.write("<span class='diagnosis malicious'>Malicious</span>", unsafe_allow_html=True)

    st.write("Probability of being benign: ", model.predict_proba(input_array_scaled)[0][0])
    st.write("Probability of being malicious: ", model.predict_proba(input_array_scaled)[0][1])


    return prediction[0]


def main():
    create_table()  # Create the table if it doesn't exist

    st.set_page_config(
        page_title="Breast Cancer Predictor",
        page_icon=":female-doctor:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    input_data = add_sidebar()

    # Create a container for the radar chart and prediction
    col1, col2 = st.columns([3, 1])  # Two columns, one for the chart and one for the prediction

    with col1:
        # Radar chart at the top
        st.title("Breast Cancer Predictor")
        st.write("This app predicts whether a tumor is benign or malignant based on various cell features.")
        radar_chart = get_radar_chart(input_data)
        st.plotly_chart(radar_chart)

    with col2:
        # Cell Cluster Prediction on the right
        diagnosis = add_predictions(input_data)

    # Create the form on the right (beneath the prediction)
    with col2:
        st.subheader("Enter your details")
        with st.form("user_form"):
            name = st.text_input("Name")
            user_id = st.text_input("ID Number")
            submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            # Get predictions
            diagnosis = add_predictions(input_data)

            # Store the data in the database
            store_user_data(name, "Malignant" if diagnosis == 1 else "Benign", input_data)

            st.write("Your data has been successfully saved.")

    # Search for user data by name
    search_name = st.text_input("Enter your name to retrieve your data:")
    if search_name:
        user_data = retrieve_user_data(search_name)
        if user_data:
            st.write("User Data Retrieved:")
            for data in user_data:
                st.write(data)
        else:
            st.write("No data found for this name.")

if __name__ == '__main__':
    main()
