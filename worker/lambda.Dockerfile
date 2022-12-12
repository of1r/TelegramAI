FROM public.ecr.aws/lambda/python:3.8
COPY . ${LAMBDA_TASK_ROOT}
RUN pip3 install -r worker/requirements.txt --target "${LAMBDA_TASK_ROOT}"
CMD [ "worker.app.lambda_handler" ]