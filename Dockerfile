FROM python:3.10

WORKDIR /app
COPY . .
# Install torch from PyTorch CPU index
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install sentence-transformers from PyPI
RUN pip install --no-cache-dir sentence-transformers

RUN pip install -r requirements.txt
CMD ["python", "run.py"]
