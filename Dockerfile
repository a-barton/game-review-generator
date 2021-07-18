FROM huggingface/transformers-pytorch-gpu

# Install miniconda
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN apt-get update
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

WORKDIR /src/src-container

# Create environment
COPY environment.yaml .
RUN conda env create -f environment.yaml

# Make new shells switch to new conda environment by default
RUN echo "source activate grg" >> ~/.bashrc
ENV PATH /opt/conda/envs/grg/bin:$PATH

# Switch shell from sh to bash
SHELL ["conda", "run", "-n", "grg", "/bin/bash", "-c"]

COPY src/src-container/ .

# Run python script to download and cache pretrained model
RUN python download_pretrained_model.py

ENTRYPOINT ["conda", "run", "-n", "grg", "python3", "generate_review.py"]