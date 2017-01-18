# Rhizome
Designed for data visualization to help eradicate polio!

Built with Python, Django, JavaScript, React, Reflux, HighCharts, and many other libraries.

## Setting up the development environment with Docker #

Download: ["Docker for Mac"](https://docs.docker.com/engine/installation/mac/) or with [Docker Toolbox](https://www.docker.com/products/docker-toolbox) and [VirtualBox](http://download.virtualbox.org/virtualbox/5.0.26/VirtualBox-5.0.26-108824-OSX.dmg)


Copy the base config to your .env and adjust any necessary passwords and keys
`$ cp .env-example .env`

Build and run the project
`$ docker-compose build && docker-compose up`



## Helpful Commands


To Enter Docker Web Server Container running Django

```
$ docker exec -it rhizome_rhizome_1 bash
```

While inside the docker web instance, migrate the database and create a superuser in order to login

```
root@4d3814881439:/rhizome# ./manage.py migrate

root@4d3814881439:/rhizome# ./manage.py createsuperuser
```

While inside the docker web instance, to run the Python Tests:

```
root@4d3814881439:/rhizome# ./manage.py test --settings=rhizome.settings.test
```

To Enter Docker DB Container running Postgres

```
$ docker exec -it rhizome_db_1 psql -U postgres
```

To enter into the gulp watcher..

```
$ docker exec -it rhizome_fe_1 sh
```


If either of these commands do not work, then please ensure you have the proper `node` and `npm` versions installed.

# Serving the Django Application with Apache.

Make sure that Apache is configured to use the
[prefork MPM](https://httpd.apache.org/docs/2.4/mpm.html); the worker and event
MPMs result in incorrect responses returned for requests when multiple requests
are made to the server.

```
sudo apt-get install apache2-mpm-prefork
```

See more [here](http://codebucket.co.in/apache-prefork-mpm-configuration/)

For more information on deploying [Django][] applications, see the
[Django documentation](https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/).

# Documentation
Start here by checking out our [documentation](http://unicef.github.io/rhizome/).

# Style
For python style guide and instructions on how to configure your editor in alignment with our linter config see the [plylintrc file](https://github.com/unicef/rhizome/blob/dev/rhizome/pylintrc)
