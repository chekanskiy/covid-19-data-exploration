FROM python:3.8-slim-buster


# https://github.com/WhitewaterFoundry/Pengwin/issues/448
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199#23
RUN mkdir -p /usr/share/man/man1

RUN apt-get -y update && apt-get install -f --no-install-recommends -y \
  curl \
  software-properties-common \
  git \
  default-jre \
#    && apt-get -y update \
#    && add-apt-repository ppa:webupd8team/java \
#    && apt-get install -y openjdk-8-jre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN  git config --global user.email "auto@commit.com" \
     && git config --global user.name "Update Bot"

#COPY ./requirements.txt /
#RUN pip install -r requirements.txt

RUN pip install \
        dash==1.12.0 \
        dash-bootstrap-components==0.10.0 \
        geopandas==0.7.0 \
        great-expectations==0.11.5 \
        json5==0.9.4 \
        jupyter==1.0.0 \
        jupyterlab==2.1.2 \
        jupyterlab-server==1.1.1 \
        pandas==1.0.3 \
        numpy==1.18.0 \
        Pillow==7.1.2 \
        plotly==4.6.0 \
        pyarrow==0.17.1 \
        python-dotenv==0.13.0 \
        PyYAML==5.3.1 \
        redis==3.5.2 \
        requests==2.23.0 \
        scikit-learn==0.22.2.post1 \
        scipy==1.4.1 \
        Shapely==1.7.0 \
        statsmodels==0.11.1 \
        tabula-py==2.1.0 \
        tabulate==0.8.7 \
        tqdm==4.46.0 \
        world-bank-data==0.1.3 \