# Use the official image as a parent image.
FROM debian

# Set the working directory.
WORKDIR /OpenCast

# Install dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -q -y \
    git sudo

# Inform Docker that the container is listening on the specified port at runtime.
EXPOSE 8080 2020

# Copy the project source
COPY . .

ENTRYPOINT ["/bin/bash"]
