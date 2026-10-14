FROM python:3.14

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY d878uvii_patcher.py /app/
COPY firmware /app/firmware/
COPY patches /app/patches/

WORKDIR /work
ENTRYPOINT ["python", "/app/d878uvii_patcher.py"]
