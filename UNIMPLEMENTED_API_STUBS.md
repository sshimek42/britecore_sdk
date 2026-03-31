# Unimplemented API Stubs

*Last updated: March 31, 2026*
*Document type: Living implementation backlog*

This document tracks API domains and calls present in `britecore_api.json`
that do not yet have implemented v2 wrappers in the SDK.

Generated stubs were added under `src/britecore_libraries/api/api_calls/v2/`
for each missing domain so the backlog is explicit and importable.

## Missing domains summary

| Domain | Stub file | Unimplemented calls |
|---|---|---:|
| `accounting` | `src/britecore_libraries/api/api_calls/v2/accounting.py` | 3 |
| `attachments` | `src/britecore_libraries/api/api_calls/v2/attachments.py` | 11 |
| `billing` | `src/britecore_libraries/api/api_calls/v2/billing.py` | 4 |
| `commissions` | `src/britecore_libraries/api/api_calls/v2/commissions.py` | 9 |
| `custom_ui` | `src/britecore_libraries/api/api_calls/v2/custom_ui.py` | 4 |
| `dashboards` | `src/britecore_libraries/api/api_calls/v2/dashboards.py` | 8 |
| `data` | `src/britecore_libraries/api/api_calls/v2/data.py` | 2 |
| `errors` | `src/britecore_libraries/api/api_calls/v2/errors.py` | 1 |
| `intacct` | `src/britecore_libraries/api/api_calls/v2/intacct.py` | 5 |
| `nightly_jobs` | `src/britecore_libraries/api/api_calls/v2/nightly_jobs.py` | 4 |
| `notifications` | `src/britecore_libraries/api/api_calls/v2/notifications.py` | 2 |
| `payments` | `src/britecore_libraries/api/api_calls/v2/payments.py` | 29 |
| `printing` | `src/britecore_libraries/api/api_calls/v2/printing.py` | 5 |
| `return_premium` | `src/britecore_libraries/api/api_calls/v2/return_premium.py` | 1 |
| `search` | `src/britecore_libraries/api/api_calls/v2/search.py` | 2 |
| `settings` | `src/britecore_libraries/api/api_calls/v2/settings.py` | 11 |
| `signatures` | `src/britecore_libraries/api/api_calls/v2/signatures.py` | 6 |
| `uploads` | `src/britecore_libraries/api/api_calls/v2/uploads.py` | 1 |
| `vendors` | `src/britecore_libraries/api/api_calls/v2/vendors.py` | 16 |

## Unimplemented calls by domain

### `accounting`

| Planned function | Method | Endpoint path |
|---|---|---|
| `get_accounting_deliverable` | `POST` | `/api/v2/accounting/get_accounting_deliverable` |
| `get_invoices` | `POST` | `/api/v2/accounting/get_invoices` |
| `run_rescind_underwriting_cancellation_pending_logic` | `POST` | `/api/v2/accounting/run_rescind_underwriting_cancellation_pending_logic` |

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

### `billing`

| Planned function | Method | Endpoint path |
|---|---|---|
| `get_installments_preview` | `POST` | `/api/v2/billing/get_installments_preview` |
| `get_installments_preview_mid_term` | `POST` | `/api/v2/billing/get_installments_preview_mid_term` |
| `get_renewal_installments_preview` | `POST` | `/api/v2/billing/get_renewal_installments_preview` |
| `rating_factors` | `POST` | `/api/v2/billing/rating_factors` |

### `commissions`

| Planned function | Method | Endpoint path |
|---|---|---|
| `delete_batch_payments` | `POST` | `/api/v2/commissions/delete_batch_payments` |
| `delete_payment` | `POST` | `/api/v2/commissions/delete_payment` |
| `get_commission_payees` | `POST` | `/api/v2/commissions/get_commission_payees` |
| `get_payment` | `POST` | `/api/v2/commissions/get_payment` |
| `get_unexported_commissions` | `POST` | `/api/v2/commissions/get_unexported_commissions` |
| `save_batch_payments` | `POST` | `/api/v2/commissions/save_batch_payments` |
| `save_batch_payments_csv` | `POST` | `/api/v2/commissions/save_batch_payments_csv` |
| `save_payment` | `POST` | `/api/v2/commissions/save_payment` |
| `update_commission_payments_complete` | `POST` | `/api/v2/commissions/update_commission_payments_complete` |

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

### `payments`

| Planned function | Method | Endpoint path |
|---|---|---|
| `makemanualpolicypayment` | `POST` | `/api/v1/payments/makeManualPolicyPayment` |
| `add_payment_method` | `POST` | `/api/v2/payments/add_payment_method` |
| `apply_selected_payments` | `POST` | `/api/v2/payments/apply_selected_payments` |
| `change_payment_method` | `POST` | `/api/v2/payments/change_payment_method` |
| `change_payment_method_single` | `POST` | `/api/v2/payments/change_payment_method_single` |
| `create_payment_batch` | `POST` | `/api/v2/payments/create_payment_batch` |
| `create_payment_entries` | `POST` | `/api/v2/payments/create_payment_entries` |
| `delete_payment_batch` | `POST` | `/api/v2/payments/delete_payment_batch` |
| `delete_payment_entries` | `POST` | `/api/v2/payments/delete_payment_entries` |
| `get_payment_method_info` | `POST` | `/api/v2/payments/get_payment_method_info` |
| `get_unpaid_invoices_by_date` | `POST` | `/api/v2/payments/get_unpaid_invoices_by_date` |
| `import_payment_entries` | `POST` | `/api/v2/payments/import_payment_entries` |
| `make_payment_by_contact_and_payment_method` | `POST` | `/api/v2/payments/make_payment_by_contact_and_payment_method` |
| `make_payment_by_invoice_or_policy` | `POST` | `/api/v2/payments/make_payment_by_invoice_or_policy` |
| `mark_payment_nsf` | `POST` | `/api/v2/payments/mark_payment_nsf` |
| `remove_payment_method` | `POST` | `/api/v2/payments/remove_payment_method` |
| `retrieve_account_payoff_amount` | `POST` | `/api/v2/payments/retrieve_account_payoff_amount` |
| `retrieve_convenience_fee` | `POST` | `/api/v2/payments/retrieve_convenience_fee` |
| `retrieve_payment` | `POST` | `/api/v2/payments/retrieve_payment` |
| `retrieve_payment_batch_entries` | `POST` | `/api/v2/payments/retrieve_payment_batch_entries` |
| `retrieve_payment_batches` | `POST` | `/api/v2/payments/retrieve_payment_batches` |
| `retrieve_payment_entries` | `POST` | `/api/v2/payments/retrieve_payment_entries` |
| `retrieve_payment_methods` | `POST` | `/api/v2/payments/retrieve_payment_methods` |
| `retrieve_policy_billing_information` | `POST` | `/api/v2/payments/retrieve_policy_billing_information` |
| `retrieve_sweep_payment_list` | `POST` | `/api/v2/payments/retrieve_sweep_payment_list` |
| `retrieve_updated_invoice_balance` | `POST` | `/api/v2/payments/retrieve_updated_invoice_balance` |
| `update_payment_batch` | `POST` | `/api/v2/payments/update_payment_batch` |
| `update_payment_entries` | `POST` | `/api/v2/payments/update_payment_entries` |
| `update_sweep_payments_complete` | `POST` | `/api/v2/payments/update_sweep_payments_complete` |

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

