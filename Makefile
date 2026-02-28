DOCKER_IMAGE := jlrgraham/losslessaudiochecker
DOCKER_IMAGE_WEB := jlrgraham/losslessaudiochecker-web

build:
	docker buildx build \
		--tag $(DOCKER_IMAGE) \
		container

build-web:
	docker buildx build \
		--tag $(DOCKER_IMAGE_WEB) \
		container-web

TEST_VOL := /Volumes/torrent/Downloads/Music/Gotye

run:
	docker run \
		-it \
		--rm \
		-e REDIS_HOST=redis.k8s.wld.n0c.io \
		--volume "$(TEST_VOL)":/input:ro \
		$(DOCKER_IMAGE)

run-web:
	docker run \
		-it \
		--rm \
		-p 5000:5000 \
		-e REDIS_HOST=redis.k8s.wld.n0c.io \
		$(DOCKER_IMAGE_WEB)
