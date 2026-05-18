# Web Pics Extractor

This project uses Python and Playwright. Here are the step-by-step instructions to set up the environment and run the script.

## 📋 Prerequisites

Make sure you have [Python](https://www.python.org/) installed on your machine.

---

## 🛠️ Installation and Setup

Open your terminal at the root of the project and run the following commands one by one:

### 1. Create the virtual environment
This command creates an isolated folder named `env` to contain the project's installations.

```
python -m venv env
```

### 2. Activate the virtual environment
Run the command that corresponds to your operating system.

**On Windows:**

```
.\env\Scripts\activate
```

**On macOS and Linux:**

```
source env/bin/activate
```

*(Once activated, you should see `(env)` at the beginning of your command line).*

### 3. Install required libraries
This command reads the `requirements.txt` file and installs the necessary dependencies (like Playwright).

```
pip install -r requirements.txt
```

### 4. Install browsers for Playwright
This command downloads the web browser binaries (Chromium, Firefox, etc.) that Playwright needs to work.

```
$env:PLAYWRIGHT_BROWSERS_PATH=".\pw-browsers"
```

**On macOS and Linux:**

```
PLAYWRIGHT_BROWSERS_PATH="./pw-browsers"
```

---

**For just the simplest way:**
```
playwright install chromium
```

**For all browsers:**
```
playwright install
```

---

## 🚀 Launch

### 5. Run the main program
Once the setup is complete, you can run the script with this command:

```
python main.py
```