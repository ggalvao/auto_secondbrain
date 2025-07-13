# Architecture

This document provides an overview of the project's architecture, including the monorepo structure, the different applications, the libraries used, and the Docker configuration.

## Monorepo Structure

The project is a monorepo with several applications under the `apps` directory and shared libraries under the `libs` directory. The `pyproject.toml` file at the root of the repository defines the workspace members using `uv`, which allows managing the dependencies for all the applications and libraries in a single place.

- `apps/`: Contains the different applications of the project.
  - `api/`: A FastAPI application that serves as the main backend.
  - `cli/`: A command-line interface.
  - `streamlit_app/`: A Streamlit application for the user interface.
- `libs/`: Contains shared libraries used by the different applications.
- `infra/`: Contains the Dockerfiles for the different services.
- `.devcontainer/`: Contains the configuration for the VS Code dev container.

## Applications

### API

The `api` application is a FastAPI application that serves as the main backend. It provides a RESTful API to interact with the system's resources.


### Streamlit App

The `streamlit_app` application is a Streamlit application that provides a user interface for the system. It interacts with the `api` application to fetch and display data.

### CLI

The `cli` application is a command-line interface that allows interacting with the system from the terminal.

## Libraries and Tools

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.11+ based on standard Python type hints.
- **Streamlit**: A faster way to build and share data apps.
- **SQLAlchemy**: The Python SQL Toolkit and Object Relational Mapper.
- **Alembic**: A lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.
- **uv**: A fast Python package installer and resolver, written in Rust.
- **pre-commit**: A framework for managing and maintaining multi-language pre-commit hooks.
- **Ruff**: An extremely fast Python linter, written in Rust.
- **Black**: The uncompromising Python code formatter.
- **isort**: A Python utility/library to sort imports alphabetically, and automatically separated into sections and by type.
- **MyPy**: Optional static typing for Python.

## Docker Configuration

The project uses Docker and Docker Compose to create a consistent and reproducible environment for development and production.

### `docker-compose.yml`

The `docker-compose.yml` file at the root of the repository defines the main services of the project:

- `postgres`: A PostgreSQL database to store the system's data.
- `api`: The FastAPI application.
- `streamlit`: The Streamlit application.

### `.devcontainer/docker-compose.dev.yml`

The `.devcontainer/docker-compose.dev.yml` file defines the `dev` service, which is used to create the development environment. This service mounts the project's source code into the container, allowing for live-reloading of the applications during development.

### `.devcontainer/devcontainer.json`

The `.devcontainer/devcontainer.json` file configures the VS Code dev container. It specifies the Docker Compose files to use, the service to connect to (`dev`), and the extensions to install in VS Code. It also defines a `postCreateCommand` that installs the project's dependencies and sets up the pre-commit hooks after the container is created.

## Development Environment

The development environment is created using the VS Code dev container feature. The dev container is built on top of the `dev` service defined in the `.devcontainer/docker-compose.dev.yml` file. This provides a consistent and isolated development environment with all the necessary tools and dependencies installed.
