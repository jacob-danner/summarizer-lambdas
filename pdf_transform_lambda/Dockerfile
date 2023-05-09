FROM public.ecr.aws/lambda/python:3.8

# Copy the requirements file and install dependencies
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Install Poppler
RUN yum install -y poppler-utils

# Add Poppler to PATH
ENV PATH="/usr/bin:${PATH}"

# Copy the app code
COPY *.py* "${LAMBDA_TASK_ROOT}"
COPY .env "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler function
CMD [ "app.lambda_handler" ]