FROM python:alpine
RUN pip install kubernetes
CMD ["python", "-u", "/auto-apply.py"]
ADD auto-apply.py /auto-apply.py
