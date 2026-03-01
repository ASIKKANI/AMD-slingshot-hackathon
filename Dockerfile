FROM rocm/pytorch:rocm5.6_ubuntu20.04_py3.8-pytorch2.0.0

WORKDIR /app

# Copy dependency file over
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Run the FastAPI server natively orchestrating agents
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
