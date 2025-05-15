launch_rockets:
	./linux_amd64/rockets launch "http://localhost:8088/messages" --message-delay=500ms --concurrency-level=1

start_server:
	python3 server.py

test:
	python -m unittest -v

test_coverage:
	coverage run -m unittest discover && coverage report -m
