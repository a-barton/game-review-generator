FROM continuumio/miniconda3

WORKDIR /src/app

# Create environment
COPY environment.yaml .
RUN apt-get install -y gunicorn
RUN conda env create -f environment.yaml && pip install --upgrade flask gunicorn joblib

# Make new shells switch to new conda environment by default
RUN echo "source activate ml-paper-topic-modelling" >> ~/.bashrc

ENV PATH /opt/conda/envs/ml-paper-topic-modelling/bin:$PATH

# Switch shell from sh to bash
SHELL ["/bin/bash", "-c"]

COPY src/app/ .
RUN chmod +X gunicorn.sh
EXPOSE 5000
ENTRYPOINT ["bash", "gunicorn.sh"]