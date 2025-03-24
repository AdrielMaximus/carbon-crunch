# carbon-crunch
 
📌 Overview

Code Quality Analyzer is a simple tool that analyzes JavaScript (React) and Python (FastAPI) code files. It gives a score based on clean code practices and suggests improvements to make your code easier to read and maintain.

# Code Quality Analyzer - Installation Guide

## 🛠 Installation (Step by Step)

### Step 1: Install Node.js
Make sure you have **Node.js** installed on your computer. You can download it from [nodejs.org](https://nodejs.org/).

### Step 2: Download the Project
Open your terminal (Command Prompt, PowerShell, or Terminal on Mac/Linux) and run:
```bash
git clone https://github.com/AdrielMaximus/carboncrunch.git
gh repo clone AdrielMaximus/carbon-crunch
```
This will download the project and navigate into its folder.

### Step 3: Install Dependencies
Run this command:
```bash
npm install
```
This project requires the following dependencies:
- **eslint**: Ensures code follows best practices.
- **prettier**: Formats code for better readability.
- **chalk**: Adds colors to the terminal output.
- **fs** (built-in): Reads and analyzes files.

To install them manually, run:
```bash
npm install eslint prettier chalk
```

### Step 4 : Set Up Backend
```
Copy
# Clone repository
git clone https://github.com/yourusername/carbon-crunch.git
cd carbon-crunch/backend

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```
### Step 5: . Set Up Frontend

```
cd ../frontend
npm install
🚀 Running the Application
Start Backend (in one terminal):
```
```
cd backend
uvicorn main:app --reload
Start Frontend (in another terminal):
```
```
cd ../frontend
npm start
Access the app at:
http://localhost:3000
```
