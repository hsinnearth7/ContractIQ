.PHONY: install generate-contracts build-index build-graph seed-demo run evaluate test lint clean

install:
	pip install -r requirements.txt

generate-contracts:
	python scripts/generate_contracts.py

build-index:
	python scripts/build_index.py

build-graph:
	python scripts/build_graph.py

seed-demo:
	python scripts/seed_demo.py

run:
	streamlit run contractiq/ui/app.py

evaluate:
	python scripts/run_evaluation.py

test:
	pytest tests/ -v --cov=contractiq

lint:
	ruff check contractiq/ tests/

clean:
	rm -rf data/chroma_db data/bm25_index.pkl __pycache__ .pytest_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
