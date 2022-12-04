FROM public.ecr.aws/lambda/python:3.8
COPY . .
RUN pip3 install -r metric-sender/requirements.txt --target "${LAMBDA_TASK_ROOT}"
COPY metric-sender/app.py ${LAMBDA_TASK_ROOT}
CMD [ "app.lambda_handler" ]