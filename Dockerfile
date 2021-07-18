FROM continuumio/miniconda3

WORKDIR /src/src-container

# Create environment
COPY environment.yaml .
RUN conda env create -f environment.yaml

# Make new shells switch to new conda environment by default
RUN echo "source activate grg" >> ~/.bashrc

ENV PATH /opt/conda/envs/grg/bin:$PATH

# Switch shell from sh to bash
SHELL ["/bin/bash", "-c"]

COPY src/src-container/ .

RUN python download_pretrained_model.py

CMD ["python", "generate_review.py"]