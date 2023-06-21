from gregabram/ubuntu-20

RUN apt-get update

RUN pip3 install django pymongo

RUN curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -

RUN  echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" |  tee /etc/apt/sources.list.d/mongodb-org-4.4.list
RUN  apt update
RUN  apt-get install -y mongodb-org mongocli procps

RUN apt install -y apache2  apache2-utils libexpat1 ssl-cert python net-tools lynx openssh-server libapache2-mod-wsgi-py3

RUN sed -i 's?/var/www/html?/var/www/vmail?' /etc/apache2/sites-available/000-default.conf 

RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo ubuntu
RUN echo 'ubuntu:ubuntu' | chpasswd

RUN a2enmod wsgi
# RUN echo 'WSGIScriptAlias /foo /var/www/vmail/test_script.py' >> /etc/apache2/apache2.conf

RUN echo 'WSGIScriptAlias /vmail /var/www/VMailServer/VMail/wsgi.py' >> /etc/apache2/apache2.conf
RUN echo 'WSGIPythonPath /var/www/VMailServer' >> /etc/apache2/apache2.conf
RUN echo 'Alias /static/ /var/www/media/' >> /etc/apache2/apache2.conf
RUN echo '<Directory /var/www/VMailServer>' >> /etc/apache2/apache2.conf
RUN echo '<Files wsgi.py>' >> /etc/apache2/apache2.conf
RUN echo 'Require all granted' >> /etc/apache2/apache2.conf
RUN echo '</Files>' >> /etc/apache2/apache2.conf
RUN echo '</Directory>' >> /etc/apache2/apache2.conf
RUN echo '<Directory /var/www/media>' >> /etc/apache2/apache2.conf
RUN echo 'Require all granted' >> /etc/apache2/apache2.conf
RUN echo '</Directory>' >> /etc/apache2/apache2.conf

# USE THIS FOR APACHE 
CMD apache2ctl -D BACKGROUND &  nohup mongod > /data/log 2>&1 &  service ssh restart &  tail -f /var/log/apache2/error.log
# IF you need a prompt in the container : CMD apache2ctl -D BACKGROUND &  nohup mongod > /data/log 2>&1 &  service ssh restart &  /bin/bash

# USE THIS FOR TESTING USING DJANGO DEVELOPMENT SERVER
# CMD nohup mongod > /data/log 2>&1 &  service ssh restart &  /bin/bash






