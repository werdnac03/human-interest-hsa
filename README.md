# human-interest-hsa

# 1) Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Initialize DB
python -c "from app import create_app; from app.extensions import db; app=create_app(); app.app_context().push(); from app import models; db.create_all(); print('DB created')"


# 3) Run Flask
python run.py
or
flask run

Flask App at http://127.0.0.1:5000

# 4) Run Streamlit:
streamlit run streamlit_frontend/Home.py 

Streamlit app at http://127.0.0.1:8501


# To Clear DB:
rm instance/hsa.sqlite
then rerun 2


