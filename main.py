venv\Scripts\activate
import os, subprocess
os.system("python data/generate_dummy_invoices.py")
os.system("python src/model/train.py")
os.system("python src/api/app.py")
subprocess.run(["venv\\Scripts\\activate.bat"], shell=True)
