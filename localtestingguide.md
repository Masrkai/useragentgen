# create a virtual env

uv venv
source .venv/bin/activate

# 1. Local editable install to test

uv pip install -e .
python -c "import useragentgen; print(useragentgen.generate())"

# 2. Build the wheel

uv pip install hatchling
python -m hatchling build
