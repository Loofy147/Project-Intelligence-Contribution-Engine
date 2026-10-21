# Contributing

## Ground rules

- Keep the first release local-first and dependency-light.
- Link recommendations to repository evidence; do not describe guesses as confirmed defects.
- Never commit generated search indexes or credentials.
- Prefer small functions, clear error messages, and tests for observable behavior.
- Avoid adding a service, database, model provider, or background worker without a demonstrated requirement.

## Local setup

~~~bash
python -m pip install -e ".[dev]"
python -m pytest
pie --help
~~~

## Change workflow

1. Describe the user-visible behavior or correctness problem.
2. Add or update tests before changing behavior where practical.
3. Run the complete test suite.
4. Update the README or architecture notes when interfaces or data formats change.
5. Summarize evidence, known limitations, and follow-up work in the change description.
