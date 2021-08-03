# Inherit Huggingface transformers-pytorch-gpu image which includes CUDA support
FROM huggingface/transformers-pytorch-gpu

# Install python dependencies
COPY requirements.txt /src/src-container/requirements.txt
RUN pip install -r /src/src-container/requirements.txt

# Set working directory used at runtime
WORKDIR /src/src-container

# Copy source code
COPY . /src/src-container/

# Set entrypoint to run main generate_review.py script
ENTRYPOINT ["python3", "generate_review.py"]