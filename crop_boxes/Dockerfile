FROM public.ecr.aws/lambda/python:3.8

# Copy the requirements file and install dependencies
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# install pytesseract
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y update
RUN yum -y install tesseract

# Copy the app code
COPY *.py* "${LAMBDA_TASK_ROOT}"
COPY .env "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler function
CMD [ "app.lambda_handler" ]