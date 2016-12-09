FROM python:2.7

RUN pip install python-telegram-bot --upgrade

ADD unni.cfg /
ADD unni.py /
RUN chmod 700 unni.py
CMD [ "./unni.py" ]
