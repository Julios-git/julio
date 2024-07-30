import streamlit as st
import matplotlib

st.title('Verificación de Versiones')

# Mostrar la versión de matplotlib
st.write(f'Versión de matplotlib: {matplotlib.__version__}')
