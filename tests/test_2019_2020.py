from azure.storage.blob import ContainerClient, BlobClient, BlobServiceClient
import zipfile
import petromodder


def test_2020(azBlobKey):
    conn_string = f"DefaultEndpointsProtocol=https;AccountName=dipvp;AccountKey={azBlobKey};EndpointSuffix=core.windows.net"
    blob = BlobClient.from_connection_string(
        conn_str=conn_string, container_name="petromodder-testdata", blob_name="2020_1.zip"
    )
    print("Downloading test 2020 model")
    with open("./2020_1.zip", "wb") as my_blob:
        blob_data = blob.download_blob()
        blob_data.readinto(my_blob)

    print("Extracting test 2020 model")
    with zipfile.ZipFile("./2020_1.zip", "r") as zip_f:
        zip_f.extractall("./")

    print("Instantiate a 2020 model")
    pm = petromodder.PetroMod(".//2020_1//pm3d//LayerCake")
    assert isinstance(pm.version, str)


def test_2019(azBlobKey):
    conn_string = f"DefaultEndpointsProtocol=https;AccountName=dipvp;AccountKey={azBlobKey};EndpointSuffix=core.windows.net"
    blob = BlobClient.from_connection_string(
        conn_str=conn_string, container_name="petromodder-testdata", blob_name="2019_1.zip"
    )

    print("Downloading test 2019 model")
    with open("./2019_1.zip", "wb") as my_blob:
        blob_data = blob.download_blob()
        blob_data.readinto(my_blob)

    print("Extracting test 2019 model")
    with zipfile.ZipFile("./2019_1.zip", "r") as zip_f:
        zip_f.extractall("./")

    print("Instantiate a 2019 model")
    pm = petromodder.PetroMod(".//2019_1//pm3d//LayerCake")
    assert pm.version == "2019.1"

