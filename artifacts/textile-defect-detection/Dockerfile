FROM python:3-alpine

RUN pip3 install paho-mqtt requests

COPY  ./src /cv-textile-defect-detection

WORKDIR /cv-textile-defect-detection

CMD ["python3","-u","mqtt_client.py"]