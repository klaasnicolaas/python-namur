<!-- Banner -->
![alt Banner of the ODP Namur package](https://raw.githubusercontent.com/klaasnicolaas/python-namur/main/assets/header_namur-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Code Quality][code-quality-shield]][code-quality]
[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]

[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]

Asynchronous Python client for the open datasets of Namur (Namen - Belgium).

## About

A python package with which you can retrieve data from the Open Data Platform of Namur via [their API][api]. This package was initially created to only retrieve parking data from the API, but the code base is made in such a way that it is easy to extend for other datasets from the same platform.

## Installation

```bash
pip install namur
```

## Datasets

You can read the following datasets with this package:

- [Parking / Parking - Emplacements][parking]

<details>
    <summary>Click here to get more details</summary>

### Parking spaces

You can use the following parameters in your request:

- **limit** (default: 10) - How many results you want to retrieve.
- **parking_type** (default: ParkingType.NORMAL) - See the list below to find the corresponding enum value.

| `ParkingType`            | Enum         |
| :----------------------- | :----------- |
| Normal parking spot      | NORMAL       |
| Garage                   | GARAGE       |
| Disabled parking spot    | PMR          |
| Drop-off spot            | DROP_OFF     |
| Delivery spot            | DELIVERY     |
| Police parking spot      | POLICE       |
| Taxi parking spot        | TAXI         |
| Car-sharing parking spot | CAR_SHARING  |
| Recycling parking spot   | RECYCLING    |
| Car parking spot         | CAR          |
| School bus parking spot  | SCHOOL_BUS   |
| Electric charging spot   | ELECTRIC_CAR |
| Reserved parking spot    | RESERVED     |

You get the following output data back with this python package:

| Variable | Type | Description |
| :------- | :--- | :---------- |
| `spot_id` | string | The id of the parking spot |
| `parking_type` | string | The type of parking of the parking spot |
| `street` | string | The street name where this parking spot is located |
| `longitude` | float | The longitude of the parking spot |
| `latitude` | float | The latitude of the parking spot |
| `created_at` | datetime | When this parking spot was created in the dataset |
| `updated_at` | datetime | When this parking spot was updated in the dataset |
</details>

## Example

```python
import asyncio

from namur import ODPNamur


async def main() -> None:
    """Show example on using the API of Namur."""
    async with ODPNamur() as client:
        parkings = await client.parking_spaces(limit=10, parking_type=1)
        print(parkings)


if __name__ == "__main__":
    asyncio.run(main())
```

## Use cases

[NIPKaart.nl][nipkaart]

A website that provides insight into where disabled parking spaces are, based
on data from users and municipalities. Operates mainly in the Netherlands, but
also has plans to process data from abroad.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.
You need at least:

- Python 3.11+
- [Poetry][poetry-install]

### Installation

Install all packages, including all development requirements:

```bash
poetry install
```

_Poetry creates by default an virtual environment where it installs all
necessary pip packages_.

### Pre-commit

This repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. To setup the pre-commit check, run:

```bash
poetry run pre-commit install
```

And to run all checks and tests manually, use the following command:

```bash
poetry run pre-commit run --all-files
```

### Testing

It uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. To run the tests:

```bash
poetry run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2022-2025 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[api]: https://data.namur.be/
[parking]: https://data.namur.be/explore/dataset/namur-parking-emplacements
[nipkaart]: https://www.nipkaart.nl

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-namur/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-namur/actions/workflows/tests.yaml
[code-quality-shield]: https://github.com/klaasnicolaas/python-namur/actions/workflows/codeql.yaml/badge.svg
[code-quality]: https://github.com/klaasnicolaas/python-namur/actions/workflows/codeql.yaml
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-namur.svg
[commits-url]: https://github.com/klaasnicolaas/python-namur/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-namur/branch/main/graph/badge.svg?token=AMVI2EVPR0
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-namur
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-namur
[downloads-shield]: https://img.shields.io/pypi/dm/namur
[downloads-url]: https://pypistats.org/packages/namur
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-namur.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-namur.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/4beb1bcd3473c5344432/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-namur/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[pypi]: https://pypi.org/project/namur/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/namur
[typing-shield]: https://github.com/klaasnicolaas/python-namur/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-namur/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-namur.svg
[releases]: https://github.com/klaasnicolaas/python-namur/releases

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
