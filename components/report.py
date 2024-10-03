import pdfkit
import os
from flask import Flask, send_file, send_from_directory

import plotly.io as pio
import base64
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import tempfile

def generate_pdf_report(titles, plotly_figures):
    # Create a PDF document in memory
    pdf_buffer = BytesIO()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for index, title in enumerate(titles):
        # Add a new page for each figure
        pdf.add_page()

        # Title of the figure
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, title, ln=True, align='C')

        # Convert the Plotly figure to a Matplotlib figure
        fig = plotly_to_matplotlib(plotly_figures[index])

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image_file:
            # Save the Matplotlib figure as a PNG file
            fig.savefig(temp_image_file.name, format='png')
            plt.close(fig)  # Close the Matplotlib figure to free memory
            
            # Insert the image into the PDF
            pdf.image(temp_image_file.name, x=10, y=30, w=180)

        # Delete the temporary image file after inserting it into the PDF
        os.remove(temp_image_file.name)
    # Save PDF to buffer (use 'S' to get the PDF as a string/bytes)
    pdf_output = pdf.output(dest='S').encode('latin1')  # FPDF uses latin1 encoding

    # Create a BytesIO buffer and write the PDF content into it
    pdf_buffer = BytesIO()
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)  # Rewind the buffer to the beginning
    
# Return the PDF buffer for further use (such as downloading in a web app)
    return pdf_buffer

def plotly_to_matplotlib(plotly_fig):
    """Convert a Plotly figure to a Matplotlib figure while preserving the chart type and adding a legend."""
    fig, ax = plt.subplots()
    
    for trace in plotly_fig['data']:
        if trace['type'] == 'bar':
            # If the trace is a bar chart
            ax.bar(trace['x'], trace['y'], label=trace['name'] if 'name' in trace else 'Series')
        
        elif trace['type'] == 'scatter':
            # If the trace is a line chart (scatter in Plotly can represent line charts)
            mode = trace.get('mode', 'lines')  # Get the mode (lines, markers, etc.)
            if mode == 'lines':
                ax.plot(trace['x'], trace['y'], label=trace['name'] if 'name' in trace else 'Series')
            elif mode == 'markers':
                ax.scatter(trace['x'], trace['y'], label=trace['name'] if 'name' in trace else 'Series')
        
        elif trace['type'] == 'pie':
            # If the trace is a pie chart
            fig, ax = plt.subplots()  # Create a new figure and axis for the pie chart
            ax.pie(trace['values'], labels=trace['labels'], autopct='%1.1f%%')
            return fig  # Return the pie chart figure immediately, as it's a standalone plot
        
        # You can add more types of charts if needed

    # Set title and axis labels from Plotly figure
    ax.set_title(plotly_fig['layout'].title.text if 'title' in plotly_fig['layout'] else "Plot",
                 loc='center', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(plotly_fig['layout'].xaxis.title.text if 'xaxis' in plotly_fig['layout'] else "X-axis")
    ax.set_ylabel(plotly_fig['layout'].yaxis.title.text if 'yaxis' in plotly_fig['layout'] else "Y-axis")
    
    ax.legend()  # Ensure that the legend is displayed based on the labels
    
    return fig