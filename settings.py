INSTALLED_APPS = [
    # Other installed apps...
    'corsheaders',  # Add this line
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]



MIDDLEWARE = [
    # Other middleware...
    'corsheaders.middleware.CorsMiddleware',  # Add this line
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
]
