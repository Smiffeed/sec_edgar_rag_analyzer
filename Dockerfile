FROM apache/airflow:3.1.8

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

USER airflow
RUN pip install --no-cache-dir \
    sec_edgar_downloader \
    chromadb \
    unstructured \
    python-dotenv

# Pre-download the NLP model to not crash unstructured lib
RUN python -m spacy download en_core_web_sm

