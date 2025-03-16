FROM  python:3.10-slim
WORKDIR /page
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
COPY page/ .
CMD ["streamlit", "run", "./main.py"]