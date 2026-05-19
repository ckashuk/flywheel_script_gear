import argparse
import json
import os
import shutil

import flywheel
import requests
from typing import Union

"""
"""

class FWSFileException(Exception):
    """
    add one or more specific exceptions now, you may ned them later@
    """
    pass

def fws_get_request_url(fw: flywheel.Client, fw_object: Union[flywheel.FileEntry, str], upload: bool = False) -> tuple[str, dict]:
    """
    # generate a url and header from the flywheel object, to open a requests call

    Parameters
    ----------
    fw: a flywheel.Client object
    fw_object: either a flywheel.Container object or a string "flywheel path" that is resolvable with fw.resolve

    Returns
    -------
    the url and headers for the given fw_object, to be used in a requests call

    """
    # TODO: 2026-05 csk currently no better way to get api_key, may revisit this later
    host = fw.get_config()['site']['api_url']
    api_key = fw._fw.api_client.configuration.api_key.get('Authorization', '')
    headers = {'Authorization': f'scitran-user {api_key}'}

    if upload:
        # for upload, fw_object should be the parent container
        url = f"{host}/{fw_object.container_type}s/{fw_object.id}/files"
    else:
        # for download, fw_object should be a FileEntry with parent_ref
        url = f"{host}/{fw_object.parent_ref['type']}s/{fw_object.parent_ref['id']}/files/{fw_object.name}"

    return url, headers


def fws_download(fw: flywheel.Client, fw_object: Union[flywheel.FileEntry, str], local_path:str) -> None:
    """
    download a flywheel object, usually a file, using http requests to allow platform access

    Parameters
    ----------
    fw: flywheel.Client
        the way to talk to flywheel. contains the host and the api key
    fw_object: a flywheel.Container object
        the flywheel object, usually a file, to download
    local_path: str
        the filesystem path to save the file to

    Returns
    -------
    None

    """
    # if fw_object is a path, resolve it to the object
    if isinstance(fw_object, str):
        fw_object = fw.resolve(fw_object)['path'][-1]

    # open with requests and the api key, flywheel generates a "ticket" to allow downloading
    url, headers = fws_get_request_url(fw, fw_object)
    with requests.get(url, headers=headers, stream=True, timeout=(10, 300)) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                if chunk:
                    f.write(chunk)


def fws_upload(fw: flywheel.Client, fw_object: Union[flywheel.FileEntry, str], local_path: str) -> None:
    """
    upload  a flywheel object, usually a file, using http requests to allow platform access

    Parameters
    ----------
    fw: flywheel.Client
        the way to talk to flywheel. contains the host and the api key
    fw_object: a flywheel.Container object
        the flywheel object, usually a file, to download
    local_path: str
        the filesystem path to save the file to

    Returns
    -------
    None

    """
    # if fw_object is a path, resolve it to the object
    if isinstance(fw_object, str):
        fw_object = fw.resolve(os.path.dirname(fw_object))['path'][-1]

    # open with requests and the api key, flywheel generates a "ticket" to allow uploading
    url, headers = fws_get_request_url(fw, fw_object, upload=True)
    filename = os.path.basename(local_path)
    with open(local_path, 'rb') as f:
        files = {'file': (filename, f, 'application/octet-stream')}
        metadata = json.dumps({'name': filename})
        data = {'metadata': metadata}
        r = requests.post(url, headers=headers, files=files, data=data, timeout=(10, 300))
        r.raise_for_status()


# the following functions are meant as usable examples of how to make use of fws_upload and fws_download in getting
# information from flywheel projects
def fws_validate_fws_files(fw) -> None:
    """
    simple test code using one of my api-keys and always-existing test objects

    Parameters
    ----------
    fw: flywheel.Client
        a valid flywheel client object, requires an api-key to create

    """
    file_fw_path_from = 'prostatespore/fws_test_project/fws_test_subject/fws_test_session/MR/Obl Axial T2 Prostate.zip'
    file_fw_path_to = 'prostatespore/fws_test_project/fws_test_subject/fws_test_session/MR/Obl Axial T2 Prostate 2.zip'

    fws_download(fw, file_fw_path_from, f'z://scratch/{os.path.basename(file_fw_path_from)}')
    shutil.copyfile(file_fw_path_from, file_fw_path_to)
    fws_upload(fw, file_fw_path_to, f'z://scratch/{os.path.basename(file_fw_path_to)}')

    # exception case: try to download a session
    # file_fw_path_bad = 'prostatespore/fws_test_project/fws_test_subject/fws_test_session'
    # fws_download(fw, file_fw_path_from, f'z://scratch/{os.path.basename(file_fw_path_from)}')

def fws_example_download_image_for_subject(fw, download_folder, project_label, subject_label, session_label, get_nii, get_dicom) -> None:
    """
    example code to download all nifti and/dr dicom files for a given subject/session

    Parameters
    ----------
    fw: flywheel.Client

    download_folder: str
        the local folder to write files to
    project_label: str
        identifier for a project (assumes identifiers exist in the flywheel database pointed to by fw!)
    subject_label: str
        identifier for a subject
    session_label: str
        identifier for a session
    get_nii: bool
        if True, download images that are .nii.gz
    get_dicom: bool
        if True, download images that are .dicom.zip

    """
    project = fw.projects.find_one(f'label={project_label}')
    session = fw.resolve(f'{project.parents["group"]}/{project_label}/{subject_label}/{session_label}')['path'][-1]
    os.makedirs(download_folder, exist_ok=True)

    for acquisition in session.acquisitions():
        for file in acquisition.files:
            if get_nii:
                if file.name.endswith('.nii.gz'):
                    fws_download(fw, file, f'{download_folder}/{file.name}')
                    print(f'{file.name} downloaded')
            if get_dicom:
                if file.name.endswith('.dcm'):
                    fws_download(fw, file, f'{download_folder}/{file.name}')
                    print(f'{file.name} downloaded')

def fws_files_simple_cli() -> None:
    """
    simple single-file command line

    """
    parser = argparse.ArgumentParser(description='Flywheel file upload/download via requests')
    parser.add_argument('command', choices=['upload', 'download'], help='Operation to perform')
    parser.add_argument('fws_path', help='Flywheel path (e.g. group/project/subject/session/acquisition/filename)')
    parser.add_argument('local_path', help='Local filesystem path')
    parser.add_argument('api_key', help='Flywheel API key')

    args = parser.parse_args()

    fw = flywheel.Client(args.api_key)

    if args.command == 'download':
        fws_download(fw, args.fws_path, args.local_path)
    elif args.command == 'upload':
        fws_upload(fw, args.fws_path, args.local_path)



if __name__ == '__main__':
    # fw = flywheel.Client('<<api-key>>', request_timeout=1000)
    # fws_example_download_image_for_subject(fw, '/home/aa-cxk023/share/scratch/download_test', 'FETS_GBM', 'HeadTreatPlan100049', '20200130', True, True)
    fws_files_simple_cli()
