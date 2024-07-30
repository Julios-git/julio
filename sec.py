import streamlit as st
import matplotlib.pyplot as plt

st.title('Prueba de matplotlib en Streamlit')

# Crear un gráfico simple
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
ax.set_title('Gráfico de prueba')

st.pyplot(fig)
