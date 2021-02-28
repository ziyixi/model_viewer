# The build-stage image:
FROM continuumio/miniconda3 AS build

# Update apt
RUN apt-get update && \
  apt-get install build-essential -y && \
  rm -rf /var/lib/apt/lists/*

# Install the package as normal:
COPY environment.yml .
RUN conda env create -f environment.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone enviornment
# in /venv:
RUN conda-pack -n model_viewer_pack -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack


# The runtime-stage image; we can use Debian as the
# base image since the Conda env also includes Python
# for us.
FROM debian:buster AS runtime

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# When image is run, run the code with the environment
# activated:
COPY . /pyapp

SHELL ["/bin/bash", "-c"]
CMD source /venv/bin/activate && \
  gunicorn -w 4 -b 0.0.0.0:5000 "pyapp:create_app()" --worker-class gevent --timeout 120
EXPOSE 5000
