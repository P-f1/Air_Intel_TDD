FROM python:3-alpine

RUN pip3 install paho-mqtt requests
RUN pip3 install opencv-python

COPY  ./src /cv-textile-defect-detection

WORKDIR /cv-textile-defect-detection

CMD ["python3","-u","mqtt_client.py"]