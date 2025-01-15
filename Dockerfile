# builder
FROM harbor.avataa.dev/avataa/devops/python:3.11.9-slim-bookworm-custom AS builder-image

USER root

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev gcc build-essential

USER worker

# install requirements
COPY pyproject.toml .
RUN uv sync --no-cache


# runner
FROM python:3.11.9-slim-bookworm AS runner-image

# envs
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y libpq-dev && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# add worker user
RUN adduser --disabled-password --gecos "" worker

# copy and activate virtual environment
COPY --from=builder-image --chown=worker:worker /home/worker/.venv /home/worker/.venv
ENV PATH="/home/worker/.venv/bin:${PATH}"

# copy project
COPY --chown=worker:worker app /home/worker/app

# login as worker user
USER worker

WORKDIR /home/worker/app

EXPOSE 8000

# run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]