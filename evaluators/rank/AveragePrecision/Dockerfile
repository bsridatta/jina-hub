FROM jinaai/jina:1.1.10

COPY . /workspace
WORKDIR /workspace

RUN pip install pytest && pytest

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]