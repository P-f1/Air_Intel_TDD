FROM python:3.6

RUN pip3 install paho-mqtt requests
RUN pip3 install opencv-python-headless==3.4.15.55

COPY  ./src /cv-textile-defect-detection

WORKDIR /cv-textile-defect-detection

CMD ["python3","-u","mqtt_client.py"]