#TODO: Pass in user permissions into test docker container
out=out/
test_dir=$(out)
test_docker_image_name=test_wow_addon_updater
test_docker_build=.docker_image_id
$(out):
	@mkdir -p out/

$(test_docker_build):
	@docker build -t $(test_docker_image_name) -f Dockerfile-test .
	@echo '$(shell docker images --filter=reference=test_wow_addon_updater --format "{{.ID}}")' >> $(test_docker_build)

.PHONY: test
test: $(test_docker_build) 
	@cp github_token test/github_token
	@docker run -v $(PWD)/app:/app/ -v $(PWD)/test:/test/ test_wow_addon_updater

.PHONY: docker
docker: $(test_docker_build)
	@docker run -itv $(PWD)/app:/app/ -v $(PWD)/test:/test/ test_wow_addon_updater bash

clean:
	@rm $(test_docker_build)
	@rm test/github_token
