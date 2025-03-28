FROM python:3.10

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir sentence-transformers
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
