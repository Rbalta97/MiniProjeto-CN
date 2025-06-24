# Use the official PHP Apache image
FROM php:8.2-apache

# Enable error reporting
RUN echo "error_reporting = E_ALL" >> /usr/local/etc/php/conf.d/errors.ini && \
    echo "display_errors = On" >> /usr/local/etc/php/conf.d/errors.ini

# Install PHP extensions
RUN docker-php-ext-install pdo pdo_mysql

# Enable Apache rewrite
RUN a2enmod rewrite

# Set working dir
WORKDIR /var/www/html

# 1️⃣ Copiar apenas os ficheiros do composer
COPY composer.json composer.lock ./

# 2️⃣ Instalar dependências
RUN apt-get update && apt-get install -y unzip git curl && \
    curl -sS https://getcomposer.org/installer | php && \
    php composer.phar install

# 3️⃣ Copiar o resto da app (depois do composer)
COPY . .

# Criar .htaccess se não existir
RUN if [ ! -f .htaccess ]; then \
    echo "Options -Indexes" > .htaccess && \
    echo "DirectoryIndex index.php" >> .htaccess && \
    echo "RewriteEngine On" >> .htaccess && \
    echo "RewriteCond %{REQUEST_FILENAME} !-f" >> .htaccess && \
    echo "RewriteCond %{REQUEST_FILENAME} !-d" >> .htaccess && \
    echo "RewriteRule ^ index.php [L]" >> .htaccess; \
    fi

# Permissões
RUN chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html

# Expor a porta
EXPOSE 80

# Iniciar apache
CMD ["apache2-foreground"]