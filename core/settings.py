import os
from pathlib import Path

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# --- إعدادات الأمان (Security) ---
SECRET_KEY = 'django-insecure-your-secret-key-here' # غيرها لو عندك مفتاح خاص
DEBUG = True # خليها True عشان نعرف الأخطاء حالياً
ALLOWED_HOSTS = ['Aksab.pythonanywhere.com', 'localhost', '127.0.0.1']

# --- التطبيقات (Apps) ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # المكتبات الخارجية
    'rest_framework',        # للتعامل مع الـ APIs
    'corsheaders',           # عشان يسمح للموبايل يكلم السيرفر
    
    # تطبيقنا الأساسي
    'logistics.apps.LogisticsConfig', 
]

# --- الـ Middleware (الترتيب مهم جداً هنا) ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # لازم يكون أول واحد
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aksab_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aksab_project.wsgi.application'

# --- قاعدة البيانات (SQLite حالياً للانتقال السهل) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- إعدادات الـ CORS (عشان تحل مشكلة الـ HTML اللي ظهرت في الفلاتر) ---
CORS_ALLOW_ALL_ORIGINS = True # بنسمح لأي جهاز يكلم السيرفر حالياً للتجربة
CORS_ALLOW_CREDENTIALS = True

# --- إعدادات الـ REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', # بنفتحها عشان نسجل أول مندوب بسهولة
    ]
}

# --- إعدادات اللغة والوقت (مظبوطة لمصر/السعودية) ---
LANGUAGE_CODE = 'ar-eg'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

# --- الملفات الثابتة ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

