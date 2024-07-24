# Mork

Mork is a microservice tool that provides an API to manage inactive users. It launches Celery tasks to:
- Warn inactive users by email that their account will be deleted after a period of time.
- Delete inactive users from the databases.

## Quick start guide (for developers)

Once you've cloned the project, it can be bootstrapped using the eponym GNU
Make target:

```
$ make bootstrap
```

Once the Docker images for the API backend and Celery workers have been built, you can start the
API backend and the Celery worker development servers using:

```
$ make run
```

The API backend will be available at:
[http://localhost:8100](http://localhost:8100)


To run tests and linters, there are commands for that! You can list them using:

```
$ make help
```


## Contributing

This project is intended to be community-driven, so please, do not hesitate to
get in touch if you have any question related to our implementation or design
decisions.

We try to raise our code quality standards and expect contributors to follow
the recommandations from our
[handbook](https://handbook.openfun.fr).

You can ensure your code is compliant by running the following commands:

- `make lint` to run the linters
- `make test` to run the tests

Note that we also provide a git pre-commit hook to ease your life:
```
make git-hook-pre-commit
```

## License

This work is released under the MIT License (see [LICENSE](./LICENSE.md)).
