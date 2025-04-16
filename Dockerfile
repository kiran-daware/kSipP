# Use an official Python base image with a specific version
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y libcap2-bin nginx

# Expose ports
EXPOSE 8080
EXPOSE 6061/udp
EXPOSE 6061
EXPOSE 6062/udp
EXPOSE 6062

# Create a non-root user with a specific UID (5678)
RUN addgroup --gid 1234 kuser && \
    adduser --system --uid 5678 --gid 1234 --disabled-password --gecos "" kuser

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

RUN chown -R kuser:kuser /app
RUN chown -R kuser:kuser /var/lib/nginx /var/log/nginx /run

# Create /app/kSipP/xml/tmp dir for tmp xml modification internally
RUN mkdir /app/kSipP/xml/tmp

# Grant necessary permissions
RUN chmod +s /app/kSipP/sipp/sipp
RUN setcap cap_net_raw=ep /app/kSipP/sipp/sipp

# # Copy the Nginx configuration
# COPY nginx.conf /etc/nginx/nginx.conf
COPY ksipp-nginx.conf /etc/nginx/sites-available/
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/ksipp-nginx.conf /etc/nginx/sites-enabled/

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to the non-root user before running the container
USER kuser

# Set the entrypoint for the container
ENTRYPOINT ["/entrypoint.sh"]
