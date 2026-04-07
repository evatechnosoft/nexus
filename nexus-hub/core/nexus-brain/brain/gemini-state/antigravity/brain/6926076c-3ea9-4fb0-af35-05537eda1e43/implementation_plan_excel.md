# Excel Request Import Implementation

The goal is to allow importing personnel requests from an Excel file that contains name, email, phone, and address information.

## Proposed Changes

### [Excel Sync]
- Modify `inventory_app/excel_sync.py` to add a new endpoint `/import-requests`.
- This endpoint will parse an uploaded Excel file, look for a sheet named "Talepler" or use the active sheet, and extract personnel info.
- For each row, it will use `_get_or_create_person` from `routers.requests` to handle personnel records and create a new `Request` in the system.

### [UI]
- Update `templates/excel_import.html` to include a section for importing requests.

## Verification Plan

### Automated Tests
- Create a script to generate a mock Excel file with dummy request data.
- Use `curl` to upload the file to the new endpoint.

### Manual Verification
- Check the "Talepler" list in the web UI to ensure the new requests appear with correct personnel details.
