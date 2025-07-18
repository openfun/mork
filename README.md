# Mork

Mork is a microservice that centralizes the management of **inactive users account** accross multiple systems. It exposes a REST API and runs asynchronous jobs via Celery to automate user lifecycle operations.
Mork supports two main primary workflows:
- **Warning inactive users** by email, informing them that their account will be deleted after a grace period.
- **Deleting inactive users** from internal systems and notifying external services to handle their own deletion logic.

## Why?

Mork was created to streamline user retention management across our ecosystem. Since we use **Open edX** as the authentication provider for all our services, its `auth_user` table is considered the source of truth for determining user activity and managing deletions consistently.

## How it works

A user is considered inactive if they have not logged in for more than *five years* (this threshold is configurable via a setting).
Mork scans the `auth_user` table from the edX datables (the source of truth) using the `last_login` field.
For each of these users, it deletes the user directly from the edX database (MySQL), cascading deletions. It attempts to remove the user from external services like Sarbacane (though full deletion is not possible due to Sarbacane API limitations).
It stores deletion candidates for other FUN services (e.g. Joanie, Ashley) to pull via the API.

Currently, external services must pull the `/users` endpoint to fetch the list of users they should delete.


> ⚠️ Note: Handling deletions in edX is particularly tricky. Since edX has no built-in deletion mechanism, Mork performs a deep introspection of the database schema to determine all dependencies on `auth_user`. Some tables are protected, blocking the complete deletion of users that have entries in those.

## Quick start guide (for developers)

Follow these steps to get Mork running locally for development:

### 1. Bootstrap the project

Clone the repository and run:

```bash
make bootstrap
```

This command builds the necessary Docker images for the API backend and Celery workers, installs dependencies and sets up the development environment.

### 2. Start the development stack

Once bootstrapped, start both the API and Celery worker with:
```bash
make run
```

By default, the API backend will be available at:
[http://localhost:8100](http://localhost:8100)


### 3. Explore available commands

You can list all useful Make commands with:
```bash
make help
```


## Deployment

Mork is deployed via a Helm chart that provisions the following components:
- A Rest API service
- A Celery worker for background tasks

> ℹ️ The Helm chart is located in the `helm/` directory of the repository.

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
