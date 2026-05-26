
import sys
import os
import flywheel

sys.path.insert(0, '/Users/CXK023/Documents/flywheel_script_gear')
from radlib.fws.fws_files import fws_upload

API_KEY = 'flywheelaz.uwhealth.org:djEl4p5F0JNRNnkuqAeuT-uzho21Cu9ny96A43jwrPg4-CdejUgXlJFPA'
# API_KEY = os.environ.get("FLYWHEEL_API_KEY")
fw = flywheel.Client(API_KEY, request_timeout=1000)

GROUP         = "datasciencecore"
PROJECT_LABEL = "szafari_Sandbox"
SUBJECT_LABEL = "Test_Subject_01"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, '..', 'data')

# Only upload these extensions
IMAGE_EXTENSIONS = {'.svs','.nii', '.nii.gz', '.dcm', '.png', '.jpg'}

# Target acquisition to upload into
subject = fw.lookup(f"{GROUP}/{PROJECT_LABEL}/{SUBJECT_LABEL}")
session = subject.sessions()[0]
acq     = session.acquisitions()[0]

fw_container_path = f"{GROUP}/{PROJECT_LABEL}/{SUBJECT_LABEL}/{session.label}/{acq.label}"

print(f"Uploading to : {fw_container_path}")
print(f"From         : {DATA_DIR}\n")

success_count = 0
skip_count    = 0
fail_count    = 0

print(DATA_DIR)
for filename in os.listdir(DATA_DIR):
    local_path = os.path.join(DATA_DIR, filename)

    # Skip directories
    if not os.path.isfile(local_path):
        continue

    # Skip non-image files
    ext = os.path.splitext(filename)[1].lower()
    if not any(filename.endswith(e) for e in IMAGE_EXTENSIONS):
        print(f"  ⊘ skipping (not an image): {filename}")
        skip_count += 1
        continue

    print(f"  ↑ uploading: {filename}")
    try:
        fws_upload(fw, fw_container_path, local_path)
        print(f"  ✓ uploaded: {filename}")
        success_count += 1
    except Exception as e:
        print(f"  ✗ failed: {filename} — {e}")
        fail_count += 1

print(f"\n{'=' * 50}")
print(f"  Uploaded : {success_count} file(s)")
print(f"  Skipped  : {skip_count} file(s)")
print(f"  Failed   : {fail_count} file(s)")
print(f"{'=' * 50}")