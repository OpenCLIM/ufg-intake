FROM python:3.8
RUN apt-get -y update
RUN apt-get -y install libgdal-dev gdal-bin
RUN pip install rasterio geopandas

COPY main.py .

ENTRYPOINT python main.py
