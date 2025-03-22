# -------------------------
# Stage 1: Build Stage
# -------------------------
FROM python:3.12-slim AS builder

# Set the working directory to /code
WORKDIR /code

# Copy the requirements file into the container.
COPY requirements.txt .


RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# -------------------------
# Stage 2: Final (Runtime) Stage
# -------------------------
FROM python:3.12-slim

# Create a non-root user "appuser" with a home directory.
RUN useradd --create-home appuser


WORKDIR /code

COPY --from=builder /install /usr/local

COPY .env .

COPY app/ app/

RUN chown -R appuser:appuser /code

RUN mkdir -p /logs && chown -R appuser:appuser /logs

RUN chmod -R u+rwx /home/appuser

USER appuser

CMD ["python", "-m", "app.run"]
