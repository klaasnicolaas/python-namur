## Python - ODP Namur Client

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]

[![Code Quality][code-quality-shield]][code-quality]
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]

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
- **parking_type** (default: 1) - See the list below to find the corresponding number.

| parking_type | number | counter |
| :----------- | :----: | :-----: |
| Place normale | 1 | Too much |
| Devant accès/garage | 2 | 5540 |
| PMR | 3 | 305 |
| Dépose-minute | 4 | 195 |
| Livraison | 5 | 80 |
| Police | 6 | 72 |
| Taxi | 7 | 30 |
| Car-sharing | 8 | 25 |
| Recyclage | 9 | 25 |
| Car | 10 | 11 |
| Bus scolaire | 11 | 6 |
| Borne électrique | 12 | 2 |
| Réservé | 13 | 1 |

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

This Python project is fully managed using the [Poetry][poetry] dependency
manager.

You need at least:

- Python 3.9+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## License

MIT License

Copyright (c) 2022 Klaas Schoute

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
[code-quality-shield]: https://img.shields.io/lgtm/grade/python/g/klaasnicolaas/python-namur.svg?logo=lgtm&logoWidth=18
[code-quality]: https://lgtm.com/projects/g/klaasnicolaas/python-namur/context:python
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-namur.svg
[commits-url]: https://github.com/klaasnicolaas/python-namur/commits/main
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-namur/branch/main/graph/badge.svg?token=AMVI2EVPR0
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-namur
[forks-shield]: https://img.shields.io/github/forks/klaasnicolaas/python-namur.svg
[forks-url]: https://github.com/klaasnicolaas/python-namur/network/members
[issues-shield]: https://img.shields.io/github/issues/klaasnicolaas/python-namur.svg
[issues-url]: https://github.com/klaasnicolaas/python-namur/issues
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-namur.svg
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-namur.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2022.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/4beb1bcd3473c5344432/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-namur/maintainability
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/namur/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/namur
[typing-shield]: https://github.com/klaasnicolaas/python-namur/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-namur/actions/workflows/typing.yaml
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-namur.svg
[releases]: https://github.com/klaasnicolaas/python-namur/releases
[stars-shield]: https://img.shields.io/github/stars/klaasnicolaas/python-namur.svg
[stars-url]: https://github.com/klaasnicolaas/python-namur/stargazers

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
