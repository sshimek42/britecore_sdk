# Unimplemented API Stubs

*Last updated: March 31, 2026*
*Document type: Living implementation backlog*

## Status: Complete ✅

All API domains previously tracked as stubs have been fully implemented
as of **March 31, 2026**. There are currently **no unimplemented endpoints**.

For the full list of implemented modules and endpoint counts, see
[`API_COVERAGE_ANALYSIS.md`](API_COVERAGE_ANALYSIS.md).

---

## Previously unimplemented domains (now complete)

| Domain | Module file | Calls implemented |
|---|---|---:|
| `attachments` | `src/britecore_libraries/api/api_calls/v2/attachments.py` | 11 |
| `custom_ui` | `src/britecore_libraries/api/api_calls/v2/custom_ui.py` | 4 |
| `dashboards` | `src/britecore_libraries/api/api_calls/v2/dashboards.py` | 8 |
| `data` | `src/britecore_libraries/api/api_calls/v2/data.py` | 2 |
| `errors` | `src/britecore_libraries/api/api_calls/v2/errors.py` | 1 |
| `intacct` | `src/britecore_libraries/api/api_calls/v2/intacct.py` | 5 |
| `nightly_jobs` | `src/britecore_libraries/api/api_calls/v2/nightly_jobs.py` | 4 |
| `notifications` | `src/britecore_libraries/api/api_calls/v2/notifications.py` | 2 |
| `printing` | `src/britecore_libraries/api/api_calls/v2/printing.py` | 5 |
| `return_premium` | `src/britecore_libraries/api/api_calls/v2/return_premium.py` | 1 |
| `search` | `src/britecore_libraries/api/api_calls/v2/search.py` | 2 |
| `settings` | `src/britecore_libraries/api/api_calls/v2/settings.py` | 11 |
| `signatures` | `src/britecore_libraries/api/api_calls/v2/signatures.py` | 6 |
| `uploads` | `src/britecore_libraries/api/api_calls/v2/uploads.py` | 1 |
| `vendors` | `src/britecore_libraries/api/api_calls/v2/vendors.py` | 16 |



## Unimplemented calls by domain

### `attachments`

| Planned function | Method | Endpoint path |
|---|---|---|
| `create_folder_in_user_folder` | `POST` | `/api/v2/attachments/create_folder_in_user_folder` |
| `delete_photo` | `POST` | `/api/v2/attachments/delete_photo` |
| `get_attachments_file_list` | `POST` | `/api/v2/attachments/get_attachments_file_list` |
| `get_file_metadata` | `POST` | `/api/v2/attachments/get_file_metadata` |
| `get_resource_photos` | `POST` | `/api/v2/attachments/get_resource_photos` |
| `move_user_file` | `POST` | `/api/v2/attachments/move_user_file` |
| `remove_attachments` | `POST` | `/api/v2/attachments/remove_attachments` |
| `rename_user_file` | `POST` | `/api/v2/attachments/rename_user_file` |
| `retrieve_attachments` | `POST` | `/api/v2/attachments/retrieve_attachments` |
| `upload_attachment_to_user_folder` | `POST` | `/api/v2/attachments/upload_attachment_to_user_folder` |
| `upload_attachment_unified` | `POST` | `/api/v2/attachments/upload_attachment_unified` |

### `custom_ui`

| Planned function | Method | Endpoint path |
|---|---|---|
| `createurloverride` | `POST` | `/api/v1/custom_ui/createURLOverride` |
| `deleteurloverride` | `POST` | `/api/v1/custom_ui/deleteURLOverride` |
| `retrieveurloverrides` | `POST` | `/api/v1/custom_ui/retrieveURLOverrides` |
| `updateurloverride` | `POST` | `/api/v1/custom_ui/updateURLOverride` |

### `dashboards`

| Planned function | Method | Endpoint path |
|---|---|---|
| `get_agency_experience_data` | `POST` | `/api/v2/dashboards/get_agency_experience_data` |
| `get_csr_data` | `POST` | `/api/v2/dashboards/get_csr_data` |
| `get_loss_ratio_chart` | `POST` | `/api/v2/dashboards/get_loss_ratio_chart` |
| `get_policy_count_data` | `POST` | `/api/v2/dashboards/get_policy_count_data` |
| `get_premium_data` | `POST` | `/api/v2/dashboards/get_premium_data` |
| `get_report_url` | `POST` | `/api/v2/dashboards/get_report_url` |
| `get_transaction_report` | `POST` | `/api/v2/dashboards/get_transaction_report` |
| `validate_loss_run` | `POST` | `/api/v2/dashboards/validate_loss_run` |

### `data`

| Planned function | Method | Endpoint path |
|---|---|---|
| `export_data_as_csv` | `POST` | `/api/v2/data/export_data_as_csv` |
| `get_available_dashboards` | `POST` | `/api/v2/data/get_available_dashboards` |

### `errors`

| Planned function | Method | Endpoint path |
|---|---|---|
| `get_internal_error` | `POST` | `/api/v2/errors/get_internal_error` |

### `intacct`

| Planned function | Method | Endpoint path |
|---|---|---|
| `get_intacct_vendor_info` | `POST` | `/api/v2/intacct/get_intacct_vendor_info` |
| `get_unexported_claim_transactions_xml` | `POST` | `/api/v2/intacct/get_unexported_claim_transactions_xml` |
| `get_unexported_return_premiums_xml` | `POST` | `/api/v2/intacct/get_unexported_return_premiums_xml` |
| `post_claim_transactions` | `POST` | `/api/v2/intacct/post_claim_transactions` |
| `post_return_premiums` | `POST` | `/api/v2/intacct/post_return_premiums` |

### `nightly_jobs`

| Planned function | Method | Endpoint path |
|---|---|---|
| `process_auto_pays` | `POST` | `/api/v2/nightly_jobs/process_auto_pays` |
| `process_cancellation_pending_or_non_renewals` | `POST` | `/api/v2/nightly_jobs/process_cancellation_pending_or_non_renewals` |
| `process_non_pays_and_cancellations` | `POST` | `/api/v2/nightly_jobs/process_non_pays_and_cancellations` |
| `process_renewals` | `POST` | `/api/v2/nightly_jobs/process_renewals` |

### `notifications`

| Planned function | Method | Endpoint path |
|---|---|---|
| `acknowledge` | `POST` | `/api/v2/notifications/acknowledge` |
| `current` | `POST` | `/api/v2/notifications/current` |


### `printing`

| Planned function | Method | Endpoint path |
|---|---|---|
| `getattachment` | `POST` | `/api/v1/printing/getAttachment` |
| `gettobeprinted` | `POST` | `/api/v1/printing/getToBePrinted` |
| `markasprinted` | `POST` | `/api/v1/printing/markAsPrinted` |
| `sendprinthawk` | `POST` | `/api/v1/printing/sendPrintHawk` |
| `sendprinthawkemail` | `POST` | `/api/v1/printing/sendPrintHawkEmail` |

### `return_premium`

| Planned function | Method | Endpoint path |
|---|---|---|
| `exportreturnpremium` | `POST` | `/api/v2/return_premium/exportReturnPremium` |

### `search`

| Planned function | Method | Endpoint path |
|---|---|---|
| `add_to_index` | `POST` | `/api/v2/search/add_to_index` |
| `remove_from_index` | `POST` | `/api/v2/search/remove_from_index` |

### `settings`

| Planned function | Method | Endpoint path |
|---|---|---|
| `add_city_to_zip_override` | `POST` | `/api/v2/settings/add_city_to_zip_override` |
| `add_counties_to_state` | `POST` | `/api/v2/settings/add_counties_to_state` |
| `add_county_to_zip_override` | `POST` | `/api/v2/settings/add_county_to_zip_override` |
| `get_pdf_engine` | `POST` | `/api/v2/settings/get_pdf_engine` |
| `get_setting_value` | `POST` | `/api/v2/settings/get_setting_value` |
| `get_system_tags_list` | `POST` | `/api/v2/settings/get_system_tags_list` |
| `retrieve_credit_permission_prompt` | `POST` | `/api/v2/settings/retrieve_credit_permission_prompt` |
| `retrieve_property_valuation_availability` | `POST` | `/api/v2/settings/retrieve_property_valuation_availability` |
| `retrieve_system_tags` | `POST` | `/api/v2/settings/retrieve_system_tags` |
| `set_pdf_engine` | `POST` | `/api/v2/settings/set_pdf_engine` |
| `set_setting_value` | `POST` | `/api/v2/settings/set_setting_value` |

### `signatures`

| Planned function | Method | Endpoint path |
|---|---|---|
| `docusign_auth` | `POST` | `/api/v2/signatures/docusign_auth` |
| `docusign_config` | `POST` | `/api/v2/signatures/docusign_config` |
| `get_signatures` | `POST` | `/api/v2/signatures/get_signatures` |
| `recreate_envelope` | `POST` | `/api/v2/signatures/recreate_envelope` |
| `update_signatures` | `POST` | `/api/v2/signatures/update_signatures` |
| `void_envelope` | `POST` | `/api/v2/signatures/void_envelope` |

### `uploads`

| Planned function | Method | Endpoint path |
|---|---|---|
| `attach_file_to_policy` | `POST` | `/api/v2/uploads/attach_file_to_policy` |

### `vendors`

| Planned function | Method | Endpoint path |
|---|---|---|
| `build_ivans_manual_claim` | `POST` | `/api/v2/vendors/build_ivans_manual_claim` |
| `build_nxtech_initial_load` | `POST` | `/api/v2/vendors/build_nxtech_initial_load` |
| `build_nxtech_manual_transactions` | `POST` | `/api/v2/vendors/build_nxtech_manual_transactions` |
| `commercial_munichre_indepth_eligibility` | `POST` | `/api/v2/vendors/commercial_munichre_indepth_eligibility` |
| `fetch_motor_vehicle_report_for_drivers` | `POST` | `/api/v2/vendors/fetch_motor_vehicle_report_for_drivers` |
| `get_aon_cat_score` | `POST` | `/api/v2/vendors/get_aon_cat_score` |
| `get_prefill_services_data` | `POST` | `/api/v2/vendors/get_prefill_services_data` |
| `get_value360_token` | `POST` | `/api/v2/vendors/get_value360_token` |
| `get_wtw_score` | `POST` | `/api/v2/vendors/get_wtw_score` |
| `invoice_cloud_autopay_enroll` | `POST` | `/api/v2/vendors/invoice_cloud_autopay_enroll` |
| `invoice_cloud_autopay_is_enrolled` | `POST` | `/api/v2/vendors/invoice_cloud_autopay_is_enrolled` |
| `invoice_cloud_suppress_insured_deliverable_printings` | `POST` | `/api/v2/vendors/invoice_cloud_suppress_insured_deliverable_printings` |
| `ivans_edocs_build` | `POST` | `/api/v2/vendors/ivans_edocs_build` |
| `ivans_file_upload` | `POST` | `/api/v2/vendors/ivans_file_upload` |
| `munichre_indepth_eligibility` | `POST` | `/api/v2/vendors/munichre_indepth_eligibility` |
| `update_value360_replacement_cost_value` | `POST` | `/api/v2/vendors/update_value360_replacement_cost_value` |

