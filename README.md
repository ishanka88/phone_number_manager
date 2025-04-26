
readme_content = """
# 📱 Phone Number Manager

A simple Flask web app to upload, store, and export phone numbers from Excel files. Duplicate numbers are ignored, and exported numbers are marked as "taken" and saved to organized folders.

---

## 📦 Features

- Upload Excel file with phone numbers (`.xlsx`)
- Auto-remove duplicates when importing
- Export selected number of phone numbers by country
- Mark exported numbers as "taken"
- Organize exports into named folders
- Web interface with live status and export confirmation

---

## 🚀 Getting Started

Follow these steps after cloning the project:

# Quick Start

git clone https://github.com/your-username/phone-number-manager.git
cd phone-number-manager

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python app.py