# Windows Setup Guide: Alumni Management System

This guide provides a clean, step-by-step process for setting up and running the Alumni Management System on a Windows environment.

## Prerequisites

Before you begin, ensure you have the following installed on your Windows machine:
1. **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/).
   > [!IMPORTANT]
   > During installation, make sure to check the box that says **"Add Python to PATH"**.

## First-Time Setup and Execution

We have included a convenience script to handle everything from creating a virtual environment, installing dependencies, and starting the server.

1. Open **File Explorer** and navigate to your project directory.
2. Double-click the `install_and_run.bat` file.
   - *Alternatively, open Command Prompt (`cmd`) or PowerShell in the directory and run `install_and_run.bat`.*
3. The script will automatically:
   - Check if Python is installed.
   - Create a virtual environment folder named `venv`.
   - Activate the virtual environment.
   - Install all required packages listed in `requirements.txt`.
   - Start the Flask web server.
4. Once the server starts, you will see output indicating it is running on `http://127.0.0.1:5000/`.
5. Open your web browser and navigate to the provided URL to access the system.

## Running the System Subsequently

After the first-time setup is completed, you do not need to install the dependencies again. To run the system in the future:

1. Open **File Explorer** and navigate to your project directory.
2. Double-click the `run.bat` file.
3. The script will automatically activate the virtual environment and start the Flask web server.

## Troubleshooting

> [!WARNING]
> **"Python is not recognized as an internal or external command"**
> This means Python is not in your system PATH. Re-run the Python installer, choose "Modify", and ensure the "Add Python to environment variables" checkbox is ticked.

> [!TIP]
> **Manually Initializing the Database**
> If you need to reset or manually initialize the database with some dummy data (e.g. creating the default Admin account), you can run the following in Command Prompt from the project directory:
> ```cmd
> call venv\Scripts\activate.bat
> python init_db.py
> ```
> The default admin login created by this script is:
> - **Email:** `admin@abc.edu`
> - **Password:** `admin123`
