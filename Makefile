APP = react_hitl_agent.api:app
HOST = 0.0.0.0
PORT = 8000
RELOAD = --reload

.PHONY: run
run:
	uv run uvicorn $(APP) --host $(HOST) --port $(PORT) $(RELOAD)

.PHONY: prod
prod:
	uv run uvicorn $(APP) --host $(HOST) --port $(PORT)
