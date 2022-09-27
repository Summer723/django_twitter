NAME = jiuzhang/twitter
# jiuzhang/twitter 就是镜像名，可以改成你自己的，格式： {随意，一般用公司名或者个人名}/{项目名}


.PHONY: build up stop logs

build:  docker-build
up: docker-compose-up
stop: docker-compose-stop
logs: docker-compose-logs

docker-build:
	docker build -t "${NAME}" .

docker-compose-up:
	docker-compose up -d

docker-compose-stop:
	docker-compose stop

docker-compose-logs:
	docker-compose logs --tail=100 -f
