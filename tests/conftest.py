import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--constr",
        action="store",
        default="None",
        help="Connection string to Azure Blob",
    )


@pytest.fixture
def constr(request):
    return request.config.getoption("--constr")
