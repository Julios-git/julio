import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Configuración de Streamlit
st.title('Análisis de Winrate de Campeones de League of Legends')

# Cargar el archivo CSV usando el cargador de archivos de Streamlit
archivo_csv = st.file_uploader("Sube tu archivo CSV", type="csv")

if archivo_csv:
    try:
        # Cargar los datos
        data = pd.read_csv(archivo_csv)

        # Mostrar las primeras filas del dataset
        st.write(data.head())

        # Verificar las columnas
        expected_columns = ['Name', 'Score', 'Role %', 'Pick %', 'Ban %', 'KDA', 'Win %']
        for col in expected_columns:
            if col not in data.columns:
                st.error(f"Falta la columna esperada: {col}")
                break

        # Seleccionar un campeón
        campeones = data['Name'].unique()
        campeon_seleccionado = st.selectbox("Selecciona un campeón", campeones)

        # Filtrar datos para el campeón seleccionado
        data_campeon = data[data['Name'] == campeon_seleccionado]

        if not data_campeon.empty:
            # Realizar la regresión lineal
            X = data_campeon[['Score', 'Role %', 'Pick %', 'Ban %', 'KDA']]
            y = data_campeon['Win %']

            # Ajustar modelo de regresión lineal
            model = LinearRegression()
            model.fit(X, y)
            predictions = model.predict(X)
            r2 = r2_score(y, predictions)

            # Graficar la regresión lineal
            plt.figure(figsize=(10, 6))
            sns.scatterplot(x='Score', y='Win %', data=data_campeon, color='blue')
            sns.lineplot(x=data_campeon['Score'], y=predictions, color='red')
            plt.title(f'Regresión Lineal: Winrate de {campeon_seleccionado}')
            plt.xlabel('Score')
            plt.ylabel('Winrate')
            plt.grid(True)
            st.pyplot(plt.gcf())
            plt.close()

            # Mostrar el valor de R²
            st.write(f'Precisión de la regresión lineal (R²) para {campeon_seleccionado}: {r2:.2f}')

            # Mostrar la tabla filtrada
            st.write(data_campeon)

        else:
            st.warning("No hay suficientes datos para realizar la regresión lineal.")

    except pd.errors.EmptyDataError:
        st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
