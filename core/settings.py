import os
from pathlib import Path

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# --- إعدادات الأمان (Security) ---
SECRET_KEY = 'django-insecure-your-secret-key-here' 
DEBUG = True # خليها True حالياً عشان تظهر لنا أي أخطاء في الكونسول

# تأكد من كتابة الدومين بحروف صغيرة كما هو في المتصفح
ALLOWED_HOSTS = ['aksab.pythonanywhere.com', 'localhost', '127.0.0.1']

# --- التطبيقات (Apps) ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # المكتبات الخارجية
    'rest_framework',        
    'corsheaders',           
    
    # تطبيق اللوجستيات الخاص بك
    'logistics.apps.LogisticsConfig',
]

# --- الـ Middleware (الترتيب مهم جداً) ---
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # يجب أن يكون الأول
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# المسار الصحيح لعناوين الـ URLs (تعديل من aksab_project إلى core)
ROOT_URLCONF = 'core.urls'

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

# المسار الصحيح لتطبيق الـ WSGI (تعديل من aksab_project إلى core)
WSGI_APPLICATION = 'core.wsgi.application'

# --- قاعدة البيانات ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- إعدادات الـ CORS ---
# بنسمح للموبايل (Flutter) يكلم السيرفر بدون قيود حالياً
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

# --- إعدادات الـ REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', 
    ]
}

# --- إعدادات اللغة والوقت ---
LANGUAGE_CODE = 'ar-eg'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

# --- الملفات الثابتة ---
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

