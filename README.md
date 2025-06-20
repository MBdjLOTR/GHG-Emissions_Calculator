Emission Calculator 🌱

An interactive dashboard for comprehensive carbon footprint tracking and visualization, specifically designed for companies as well as individual use. This tool provides detailed analysis of Scope 1, Scope 2, and Scope 3 emissions through intuitive visualizations and data insights.

🎯 Project Overview
The Emission Calculator is a comprehensive carbon footprint management system that enables organizations to:

Track emissions across all three GHG Protocol scopes

Visualize data through interactive charts and graphs

Monitor trends in organizational carbon footprint

Generate insights for sustainability decision-making

Support compliance with environmental reporting standards

📊 Emission Scopes Covered

🏭 Scope 1 - Direct Emissions

On-site fuel combustion

Company-owned vehicles

Refrigerant leaks

Process emissions

⚡ Scope 2 - Indirect Energy Emissions

Purchased electricity

Purchased steam/heating

Purchased cooling

🌐 Scope 3 - Other Indirect Emissions

Business travel

Employee commuting

Purchased goods and services

Waste generated in operations

Upstream/downstream activities

✨ Features

📈 Interactive Dashboard - Real-time emission tracking and visualization

📊 Multiple Chart Types - Bar charts, line graphs, pie charts, and trend analyses

🎯 Scope-wise Analysis - Detailed breakdown by emission categories

📅 Time-series Tracking - Monitor emissions over time periods

📋 Data Input Interface - Easy data entry and management

📊 Comparative Analysis - Year-over-year and period-over-period comparisons

📱 Responsive Design - Works on desktop, tablet, and mobile devices

📄 Report Generation - Export detailed emission reports

🎨 Customizable Views - Flexible visualization options

Running the Emission Calculator

Prerequisites: Python 3.7 or higher, pip package manager

Installation & Setup

1) Clone the repository: git clone <repository-url>

2) cd emission-calculator

3) Install dependencies using Git Bash: pip install -r requirements.txt

4) Run the application: streamlit run app.py

5)Access the app: Open your browser and navigate to http://localhost:8501. The emission calculator interface will load automatically

Deployment Options

1) Local Development: streamlit run app.py --server.port 8501
  
2) Production Deployment: Streamlit Cloud: Connect your GitHub repository at share.streamlit.io

3) Heroku: Add setup.sh and Procfile for Heroku deployment
   
4) Docker: Use the provided Dockerfile for containerized deployment

Troubleshooting: Ensure all dependencies are installed: pip install streamlit pandas numpy. Check Python version compatibility. Verify port 8501 is available.

