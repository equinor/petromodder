import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--azBlobKey",
        action="store",
        default="None",
        help="Access key to Azure Blob",
    )


@pytest.fixture
def azBlobKey(request):
    return request.config.getoption("--azBlobKey")
