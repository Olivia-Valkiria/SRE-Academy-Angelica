FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
COPY . .
RUN pip install -r requirements.txt
RUN pip install python-dotenv
RUN pip install flask
CMD ["flask", "run", "--host", "0.0.0.0"]