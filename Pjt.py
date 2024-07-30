import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

class ETLApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Proceso ETL")
        self.master.geometry("800x400")

        self.folder_path = tk.StringVar()
        self.col_range = tk.StringVar()
        self.start_row = tk.StringVar()

        tk.Label(master, text="Carpeta de datos:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(master, textvariable=self.folder_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text="Seleccionar", command=self.select_folder).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(master, text="Rango de columnas (ej. A:C):").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(master, textvariable=self.col_range).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(master, text="Fila inicial:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(master, textvariable=self.start_row).grid(row=2, column=1, padx=5, pady=5)

        tk.Button(master, text="Procesar", command=self.process_files).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(master, text="Generar Gráficos", command=self.show_column_selection).grid(row=3, column=2, padx=5, pady=5)

        self.progress = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        self.result_text = tk.Text(master, height=10, width=70)
        self.result_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def process_files(self):
        try:
            folder = self.folder_path.get()
            col_range = self.col_range.get()
            start_row = int(self.start_row.get())

            if not folder or not col_range or not start_row:
                raise ValueError("Por favor, complete todos los campos.")

            excel_files = [f for f in os.listdir(folder) if f.endswith('.xlsx')]
            
            if not excel_files:
                raise FileNotFoundError("No se encontraron archivos Excel en la carpeta seleccionada.")

            all_data = []
            self.progress["maximum"] = len(excel_files)

            for i, file in enumerate(excel_files):
                file_path = os.path.join(folder, file)
                
                match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', file)
                if match:
                    year, month, day = match.groups()
                else:
                    raise ValueError(f"Formato de nombre de archivo inválido: {file}")

                df = pd.read_excel(file_path, sheet_name="ITEM_O", usecols=col_range, skiprows=start_row-1)
                
                df['Año'] = year
                df['Mes'] = month
                df['Día'] = day

                all_data.append(df)
                self.progress["value"] = i + 1
                self.master.update_idletasks()

            final_df = pd.concat(all_data, ignore_index=True)

            documents_path = os.path.expanduser("~/Documents")
            etl_folder = os.path.join(documents_path, "Proceso ETL")
            os.makedirs(etl_folder, exist_ok=True)

            output_path = os.path.join(etl_folder, "Out.xlsx")
            final_df.to_excel(output_path, index=False)

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Proceso completado. Se han procesado {len(excel_files)} archivos.\n")
            self.result_text.insert(tk.END, f"Dimensiones del DataFrame final: {final_df.shape}\n")
            self.result_text.insert(tk.END, "Primeras 5 filas del DataFrame:\n")
            self.result_text.insert(tk.END, final_df.head().to_string())

            messagebox.showinfo("Éxito", f"Proceso ETL completado. Los datos se han guardado en '{output_path}'")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_column_selection(self):
        try:
            documents_path = os.path.expanduser("~/Documents")
            etl_folder = os.path.join(documents_path, "Proceso ETL")
            output_path = os.path.join(etl_folder, "Out.xlsx")
            df = pd.read_excel(output_path)

            column_window = tk.Toplevel(self.master)
            column_window.title("Seleccionar Columnas")
            column_window.geometry("400x300")

            self.tree = ttk.Treeview(column_window, columns=("Column",), show="headings")
            self.tree.heading("Column", text="Columnas Disponibles")
            self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            for column in df.columns:
                self.tree.insert("", tk.END, values=(column,))

            tk.Button(column_window, text="Generar Gráficos", command=lambda: self.generate_graphs(self.tree.selection(), df)).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_graphs(self, selected_items, df):
        if len(selected_items) < 2:
            messagebox.showerror("Error", "Por favor, seleccione al menos dos columnas.")
            return

        columns = [self.tree.item(item)['values'][0] for item in selected_items]
        
        # Filtrar solo las columnas numéricas
        numeric_columns = df[columns].select_dtypes(include=['int64', 'float64']).columns
        
        if len(numeric_columns) < 2:
            messagebox.showerror("Error", "Por favor, seleccione al menos dos columnas numéricas.")
            return

        averages = df[numeric_columns].mean()

        graph_window = tk.Toplevel(self.master)
        graph_window.title("Gráficos")
        graph_window.geometry("1800x600")

        # Gráfico de barras
        fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
        averages.plot(kind='bar', ax=ax_bar)
        ax_bar.set_title("Promedio por columna (Gráfico de Barras)")
        ax_bar.set_ylabel("Promedio")
        ax_bar.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        # Gráfico de torta
        fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
        ax_pie.pie(averages, labels=averages.index, autopct='%1.1f%%', startangle=90)
        ax_pie.set_title("Distribución de Promedios (Gráfico de Torta)")
        plt.tight_layout()

        # Gráfico de distribución (histograma)
        fig_dist, ax_dist = plt.subplots(figsize=(6, 4))
        for column in numeric_columns:
            ax_dist.hist(df[column], bins=20, alpha=0.5, label=column)
        ax_dist.set_title("Distribución de Valores (Histograma)")
        ax_dist.set_xlabel("Valor")
        ax_dist.set_ylabel("Frecuencia")
        ax_dist.legend()
        plt.tight_layout()

        # Mostrar gráficos en la ventana
        canvas_bar = FigureCanvasTkAgg(fig_bar, master=graph_window)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_pie = FigureCanvasTkAgg(fig_pie, master=graph_window)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_dist = FigureCanvasTkAgg(fig_dist, master=graph_window)
        canvas_dist.draw()
        canvas_dist.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Guardar gráficos por separado
        documents_path = os.path.expanduser("~/Documents")
        etl_folder = os.path.join(documents_path, "Proceso ETL")
        bar_graph_path = os.path.join(etl_folder, "grafico_barras.png")
        pie_graph_path = os.path.join(etl_folder, "grafico_torta.png")
        dist_graph_path = os.path.join(etl_folder, "grafico_distribucion.png")

        fig_bar.savefig(bar_graph_path)
        fig_pie.savefig(pie_graph_path)
        fig_dist.savefig(dist_graph_path)

        messagebox.showinfo("Éxito", f"Gráficos guardados como:\n{bar_graph_path}\n{pie_graph_path}\n{dist_graph_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ETLApp(root)
    root.mainloop()