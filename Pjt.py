import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Configuración de Streamlit
st.title('Análisis de Emisiones de CO2 por Año')

# Cargar el archivo CSV usando el cargador de archivos de Streamlit
archivo_csv = st.file_uploader("Sube tu archivo CSV", type="csv")

if archivo_csv:
    try:
        # Cargar los datos
        data = pd.read_csv(archivo_csv)

        # Mostrar las primeras filas del dataset
        st.write("Datos cargados:")
        st.write(data.head())

        # Verificar que las columnas necesarias existan
        if 'Entity' not in data.columns or 'Year' not in data.columns or 'Value_co2_emissions_kt_by_country' not in data.columns:
            st.error("El archivo debe contener las columnas 'Entity', 'Year', y 'Value_co2_emissions_kt_by_country'.")
            st.stop()

        # Selección del país
        countries = data['Entity'].unique()
        selected_country = st.selectbox("Selecciona un país", countries)

        # Filtrar datos para el país seleccionado
        country_data = data[data['Entity'] == selected_country]

        if not country_data.empty:
            # Limpiar los datos: eliminar filas con valores faltantes en las columnas relevantes
            country_data = country_data[['Year', 'Value_co2_emissions_kt_by_country']].dropna()

            # Verificar si hay datos suficientes para la regresión
            if country_data.empty:
                st.warning(f"No hay datos válidos para el país seleccionado: {selected_country}.")
            else:
                # Renombrar las columnas para mostrar en la tabla
                country_data = country_data.rename(columns={
                    'Year': 'Año',
                    'Value_co2_emissions_kt_by_country': 'CO2 en Kilotones'
                })

                # Función para graficar la regresión lineal
                def plot_regression(data, x_col, y_col, title):
                    X = data[[x_col]].values
                    y = data[y_col].values
                    model = LinearRegression()
                    model.fit(X, y)
                    predictions = model.predict(X)
                    r2 = r2_score(y, predictions)
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.scatterplot(x=X.flatten(), y=y, color='blue', label='Datos')
                    sns.lineplot(x=X.flatten(), y=predictions, color='red', label='Regresión Lineal')
                    ax.set_title(f"{title} (R² = {r2:.2f})")
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.grid(True)
                    ax.legend()
                    st.pyplot(fig)

                # Mostrar gráfica de regresión para el país seleccionado
                st.write(f"### Regresión Lineal de Emisiones de CO2 para {selected_country}")
                if 'Año' in country_data.columns and 'CO2 en Kilotones' in country_data.columns:
                    plot_regression(country_data, 'Año', 'CO2 en Kilotones', f"Emisiones de CO2 vs Año para {selected_country}")

                # Mostrar la tabla con columnas renombradas
                st.write("### Datos del País Seleccionado")
                st.write(country_data)

        else:
            st.warning(f"No hay datos disponibles para el país seleccionado: {selected_country}.")

    except pd.errors.EmptyDataError:
        st.error("El archivo está vacío. Por favor, verifique el contenido del archivo.")
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
