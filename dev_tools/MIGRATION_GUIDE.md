# Migration Guide from Legacy Modules

This guide helps transition from legacy module paths to the new ones.

## Migration Status: COMPLETED ✅

As of the latest run of the cleanup script, no code in the project is using legacy module imports. All code has been successfully migrated to use the new module structure.

## Module Path Changes

| Legacy Module Path | New Module Path |
|-------------------|----------------|
| adapter_scanner.scanner_utils | utilities.scanner_utils |
| adapter_scanner.base_adapter | adapters.base_adapter |
| adapter_scanner.adapter_bc125at | adapters.uniden.bc125at_adapter |
| adapter_scanner.adapter_bcd325p2 | adapters.uniden.bcd325p2_adapter |
| library_scanner.bcd325p2_command_library | command_libraries.uniden.bcd325p2_commands |
| scanner_adapters.baseAdapter | adapters.base_adapter |
| scanner_adapters.bc125atAdapter | adapters.uniden.bc125at_adapter |
| scanner_adapters.bcd325p2Adapter | adapters.uniden.bcd325p2_adapter |
| scanner_adapters.sds100Adapter | adapters.uniden.sds100_adapter |

## How to Check Your Code

Run the cleanup script to find any legacy module imports:

```bash
python cleanup_legacy.py
```

## Recent Fixes

- Added missing `machineMode` attribute to `BCD325P2Adapter` class to fix "read frequency" command
- Added redirects for any remaining code in `scanner_adapters` folder to the `adapters` folder

## Removing Legacy Redirects

Since the migration is complete, the following legacy redirector files can now be safely removed:

1. `adapter_scanner/scanner_utils.py`
2. `adapter_scanner/base_adapter.py`
3. `adapter_scanner/adapter_bc125at.py`
4. `adapter_scanner/adapter_bcd325p2.py`
5. `adapter_scanner/scanner_utils_uniden.py`
6. `library_scanner/bcd325p2_command_library.py`
7. All files in the `scanner_adapters` folder

### Recommended Removal Process

1. Create a backup or ensure all changes are committed to version control
2. Remove the legacy files
3. Run all tests to ensure nothing breaks
4. If any issues occur, check for any imports that the cleanup script may have missed

### Recommended Timeline

- **Testing Phase**: 1-2 weeks with the redirects still in place
- **Removal**: After the testing phase confirms no issues
- **Version Bump**: Increase the minor version number after removal to indicate the breaking change

## Benefits of Removal

- Cleaner codebase with less redundancy
- Clear module structure
- Reduced maintenance overhead
- Smaller package size
