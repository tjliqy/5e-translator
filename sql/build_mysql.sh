#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker stop mysql-5e
docker rm mysql-5e
docker run -itd --name mysql-5e -p 3309:3306 -v "${DIR}/create_mysql.sql":"/tmp/init.sql" -e MYSQL_ROOT_PASSWORD=123456 mysql
sleep 20

docker exec -it mysql-5e mysql -uroot -p123456 -e "source /tmp/init.sql"