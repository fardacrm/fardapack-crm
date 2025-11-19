1. از یک تصویر پایه پایتون شروع می‌کنیم

FROM python:3.11-slim

2. متغیرهای محیطی

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app
WORKDIR $APP_HOME

3. نصب Node.js و NPM برای بیلد فرانت‌اند

RUN apt-get update && apt-get install -y nodejs npm

4. کپی کردن سورس فرانت‌اند برای بیلد (فقط سورس)

COPY frontend $APP_HOME/frontend

اگر requirements.txt در ریشه است، آن را نیز کپی کنید

COPY requirements.txt $APP_HOME

5. نصب وابستگی‌های پایتون

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

6. بیلد کردن فرانت‌اند (Vue.js)

RUN cd frontend && npm install && npm run build

(پوشه dist اکنون در $APP_HOME/frontend/dist قرار دارد)

7. انتقال محتویات Build شده به ریشه کانتینر

COPY main.py $APP_HOME
COPY crm.db $APP_HOME

انتقال خروجی dist به ریشه برنامه

RUN mv $APP_HOME/frontend/dist $APP_HOME/dist

8. دستوری که سرور را اجرا می‌کند

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]