FROM python:3.9

RUN pip3 install paho-mqtt requests
RUN pip3 install opencv-python-headless

COPY  ./src /cv-textile-defect-detection

WORKDIR /cv-textile-defect-detection

CMD ["python3","-u","mqtt_client.py"]