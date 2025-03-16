FROM python:3.10-slim

WORKDIR /api
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ .

EXPOSE 8000
# Run the FastAPI application using uvicorn server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
#, "--host", "127.0.0.1" , "--port", "8000"

#CMD ["fastapi", "run", "api.py", "--port", "80"]