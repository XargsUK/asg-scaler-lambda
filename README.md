<p align="center">
  <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-aws-open.svg" width="100" />
</p>
<p align="center">
    <h1 align="center">ASG Scaler</h1>
</p>
<p align="center">
    <em>Blue/Green CodeDeployments for Frugal Architects</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/XargsUK/asg-scaler-lambda?style=flat&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/XargsUK/asg-scaler-lambda?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/XargsUK/asg-scaler-lambda?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/XargsUK/asg-scaler-lambda?style=flat&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
		<em>Developed with the software and tools below.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Poetry-60A5FA.svg?style=flat&logo=Poetry&logoColor=white" alt="Poetry">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
	<img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat&logo=Pytest&logoColor=white" alt="Pytest">
</p>
<hr>

##  Quick Links

> - [ Overview](#overview)
> - [ Features](#features)
> - [ Repository Structure](#repository-structure)
> - [ Modules](#modules)
> - [ Getting Started](#getting-started)
>   - [ Installation](#installation)
>   - [Running asg-scaler](#running-asg-scaler)
>   - [ Tests](#tests)
> - [ Project Roadmap](#project-roadmap)
> - [ Contributing](#contributing)
> - [ License](#license)
> - [ Acknowledgments](#acknowledgments)

---

##  Overview

`asg-scaler` simplifies AWS Auto Scaling Groups (ASGs) management for CodePipeline CodeDeploy deployments, enabling efficient blue/green deployment strategies without requiring excess instances. Traditionally, ASGs aim to maintain a fixed capacity, complicating blue/green deployments as they necessitate doubling the instance count temporarily. asg-scaler resolves this by dynamically adjusting ASG capacities to match the deployment phase, increasing for new deployments and reverting once stability is achieved.

Read a little bit more about why this project was created - [Medium: Blue/Green Deployments: A Guide for Frugal Architects](https://medium.com/@xargsuk/streamlining-aws-blue-green-deployments-a-guide-for-frugal-architects-68ac645a9a56)

---

##  Features

|    | Feature          | Description |
|----|------------------|--------------------------------------------------------------------|
| ⚙️  | **Architecture** | This project utilises AWS Lambda for auto-scaling AWS ASGs. It's designed to dynamically adjust ASG sizes and integrates with AWS CodePipeline for deployment automation. |
| 🔩 | **Code Quality** | Adheres to PEP8 guidelines, enforced by flake8 and pylint. The code is structured around modular Python scripts, enhancing readability and maintainability. |
| 📄 | **Documentation**| Each main script and workflow is well-documented, explaining their roles within the auto-scaling and CI/CD process, though additional user guides or API docs could enhance usability. |
| 🔌 | **Integrations** | Integrates with AWS services like Lambda, Auto Scaling Groups, and CodePipeline. GitHub Actions is used for CI/CD, ensuring automated testing and deployment. |
| 🧩 | **Modularity**   | The project is modular, with distinct components for ASG management, CodePipeline interaction, and CI/CD automation, allowing for easy updates and scalability. |
| 🧪 | **Testing**      | Uses pytest and pytest-cov for running tests and measuring code coverage, ensuring reliability and functionality across updates. |
| 📦 | **Dependencies** | Depends on `boto3` for AWS interactions, `pytest`, `pytest-cov`, and `coverage` for testing, and `flake8` for linting. Managed with `poetry` for dependency resolution. |
| 🚀 | **Scalability**  | Highly scalable, leveraging AWS Lambda and ASG capabilities to dynamically adjust infrastructure based on demand, within the architectural limits of those services. |

---

##  Repository Structure

```sh
└── asg-scaler-lambda/
    ├── .github
    │   ├── scripts
    │   │   └── update_version.py
    │   └── workflows
    │       ├── build.yml
    │       ├── dry-run-release.yml
    │       └── release.yml
    ├── LICENSE
    ├── README.md
    ├── asg_scaler_lambda
    │   ├── asg_helper.py
    │   ├── asg_scaler.py
    │   └── codepipeline_event.py
    ├── poetry.lock
    ├── pylintrc
    ├── pyproject.toml
    ├── sonar-project.properties
    └── tests
        ├── test_asg_helper.py
        ├── test_asg_scaler.py
        └── test_codepipeline_event.py
```

---

##  Modules

<details closed><summary>.</summary>

| File                                                                                      | Summary                                                                                                                                                                                                                                                                                                                             |
| ---                                                                                       | ---                                                                                                                                                                                                                                                                                                                                 |
| [pylintrc](https://github.com/XargsUK/asg-scaler-lambda/blob/master/pylintrc)             | The `pylintrc` file defines linting rules for the `asg-scaler` repository, aiming to enforce code quality standards and error prevention across the Python modules.
| [pyproject.toml](https://github.com/XargsUK/asg-scaler-lambda/blob/master/pyproject.toml) | This `pyproject.toml` configures the asg-scaler-lambda project, defining dependencies, build settings, and test configurations.                                                                                  |
| [poetry.lock](https://github.com/XargsUK/asg-scaler-lambda/blob/master/poetry.lock)       |  A record of all the exact versions of the dependencies used in `asg-scaler`                                                                 |

</details>

<details closed><summary>asg_scaler_lambda</summary>

| File                                                                                                                      | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---                                                                                                                       | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| [asg_scaler.py](https://github.com/XargsUK/asg-scaler-lambda/blob/master/asg_scaler_lambda/asg_scaler.py)                 | The `asg_scaler.py` is the entrypoint of `asg-scaler`, aimed at handling AWS events to dynamically adjust Auto Scaling Group (ASG) parameters and manage CodePipeline approvals. It processes CodePipeline job events to update ASG configurations based on user parameters and handles EventBridge events to automate CodePipeline approvals.                |
| [asg_helper.py](https://github.com/XargsUK/asg-scaler-lambda/blob/master/asg_scaler_lambda/asg_helper.py)                 | `asg_helper.py` provides utility functions to update and validate Auto Scaling Group capacities in AWS. It chiefly transforms capacity parameters, ensures their logical consistency, and interfaces with AWS to adjust ASG settings.                                        |
| [codepipeline_event.py](https://github.com/XargsUK/asg-scaler-lambda/blob/master/asg_scaler_lambda/codepipeline_event.py) | `codepipeline_event.py` interfaces with AWS CodePipeline for managing job states and approvals. It provides functions to report job success or failure, approve deployment actions automatically, and retrieve necessary tokens for approvals.  |

</details>

<details closed><summary>.github.scripts</summary>

| File                                                                                                            | Summary                                                                                                                                                                                                                                                                                                |
| ---                                                                                                             | ---                                                                                                                                                                                                                                                                                                    |
| [update_version.py](https://github.com/XargsUK/asg-scaler-lambda/blob/master/.github/scripts/update_version.py) | `update_version.py` automates version updates in the project's `pyproject.toml`, ensuring consistent versioning across the `asg-scaler-lambda` repository.  |

</details>

<details closed><summary>.github.workflows</summary>

| File                                                                                                                  | Summary                                                                                                                                                                                                                                                                 |
| ---                                                                                                                   | ---                                                                                                                                                                                                                                                                     |
| [build.yml](https://github.com/XargsUK/asg-scaler-lambda/blob/master/.github/workflows/build.yml)                     | `.github/workflows/build.yml` automates build tests.                                     |
| [release.yml](https://github.com/XargsUK/asg-scaler-lambda/blob/master/.github/workflows/release.yml)                 | `release.yml`  automates versioning and deployment of the `asg-scaler-lambda` project.                                                                    |
| [dry-run-release.yml](https://github.com/XargsUK/asg-scaler-lambda/blob/master/.github/workflows/dry-run-release.yml) | This YAML file automates pre-release verifications for the asg-scaler-lambda repository. |

</details>

---

##  Getting Started

***Requirements***

Ensure you have the following dependencies installed on your system:

* **Python**: `version 3.8+`
* **Poetry**: `version 1.8.2+`

###  Installation

1. Clone the asg-scaler-lambda repository:

```sh
git clone https://github.com/XargsUK/asg-scaler-lambda
```

2. Change to the project directory:

```sh
cd asg-scaler-lambda
```

3. Install the dependencies with Poetry:

```sh
poetry install
```

###  Running `asg-scaler`

Use the following command to run asg-scaler:

```sh
poetry run python asg_scaler.py
```

###  Tests

Use the following command to run tests:

```sh
poetry run pytest
```

---

##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/XargsUK/asg-scaler-lambda/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Report Issues](https://github.com/XargsUK/asg-scaler-lambda/issues)**: Submit bugs found or log feature requests for the `asg-scaler-lambda` project.

<details closed>
    <summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/XargsUK/asg-scaler-lambda
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.

</details>

---

##  License

This project is protected under the [MIT](https://choosealicense.com/licenses/mit/) License.


---
