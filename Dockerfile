# Use an official Python base image with a specific version
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y libcap2-bin nginx

# Expose ports
EXPOSE 8000
EXPOSE 6061/udp
EXPOSE 6061
EXPOSE 6062/udp
EXPOSE 6062

# Create a non-root user with a specific UID (5678)
RUN adduser --system --uid 5678 --disabled-password --gecos "" appuser

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Grant necessary permissions
RUN chmod +s /app/kSipP/sipp/sipp
RUN setcap cap_net_raw=ep /app/kSipP/sipp/sipp
RUN chown -R 5678:5678 /app
RUN chown -R 5678:5678 /var/lib/nginx /var/log/nginx /run

# # Copy the Nginx configuration
# COPY nginx.conf /etc/nginx/nginx.conf
COPY ksipp-nginx.conf /etc/nginx/sites-available/
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/ksipp-nginx.conf /etc/nginx/sites-enabled/

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to the non-root user before running the container
USER appuser

# Set the entrypoint for the container
ENTRYPOINT ["/entrypoint.sh"]