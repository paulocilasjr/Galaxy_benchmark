FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src
COPY tools /app/tools
COPY tests /app/tests
COPY docs /app/docs
COPY experiments /app/experiments
COPY ground_truth /app/ground_truth
COPY dataset /app/dataset
COPY SKILL.md AGENTS.md /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-build-isolation -e .

CMD ["python", "-m", "unittest", "discover", "-s", "tests/unit", "-v"]
