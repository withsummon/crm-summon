FROM frappe/bench:latest

WORKDIR /workspace

COPY . /workspace

ENV SHELL=/bin/bash

EXPOSE 8000 9000

CMD ["bash", "/workspace/init.sh"]
