FROM python

WORKDIR /GPC_TOOL

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python", "./main.py" ]