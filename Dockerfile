FROM continuumio/miniconda

WORKDIR /src/src-container

RUN conda create -n grg

RUN conda install boto3

RUN echo "source activate grg" >> ~/.bashrc

ENV PATH /opt/conda/envs/grg/bin:$PATH

SHELL ["/bin/bash", "-c"]

COPY src/src-container/ .

CMD ["python", "generate_review.py"]