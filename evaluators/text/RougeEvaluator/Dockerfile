FROM jinaai/jina:1.1.9

COPY . /workspace
WORKDIR /workspace

RUN pip install -r requirements.txt

RUN pip install pytest && pytest

ENTRYPOINT ["jina", "pod", "--uses", "config.yml"]