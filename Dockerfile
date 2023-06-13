# pull python 3.6 alpine image
FROM python:3.6-alpine

# expose port 5000
EXPOSE 5000

# copy source files into workdir
ADD ./requirements.txt $WORKDIR/

# pip install requirements
RUN pip install pypandoc==1.5
RUN pip install -r ./requirements.txt

# install graphviz executable
RUN apk update && apk add graphviz

# copy source files into workdir
ADD . $WORKDIR/

# set python path
ENV PYTHONPATH="$WORKDIR:/"

# run the application
CMD ["python", "./api/main.py"]
