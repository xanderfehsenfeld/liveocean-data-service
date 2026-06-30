# [START cloudrun_django_procfile_migrate]
# Apply database migrations
uv run python manage.py migrate && python manage.py collectstatic --verbosity 2 --no-input
# [END cloudrun_django_procfile_migrate]

# [START cloudrun_django_procfile_superuser]
# Create superuser (requires DJANGO_SUPERUSER_PASSWORD and DJANGO_SUPERUSER_EMAIL envvars)
uv run python manage.py createsuperuser --username admin --noinput || echo "User already exists."
# [END cloudrun_django_procfile_superuser]

# Default entrypoint: run Django
uv run gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 liveocean_data_service.wsgi:application
