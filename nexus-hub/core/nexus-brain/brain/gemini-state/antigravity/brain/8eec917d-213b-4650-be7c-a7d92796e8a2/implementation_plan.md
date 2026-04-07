# Plan to Fix `mcp_config.json`

The current configuration in `mcp_config.json` has two issues:
1. It uses a `path` property inside an MCP server definition, which is not supported by the MCP schema.
2. Several server definitions (`cloudrun`, `firebase-mcp-server`) are at the top level of the JSON file instead of being inside the `mcpServers` object.

## Proposed Changes

### Configuration
#### [MODIFY] [mcp_config.json](file:///c:/Users/Deacjx/.gemini/antigravity/mcp_config.json)
- Remove the `"path"` property from `dart-mcp-server`.
- Update the `"command"` for `dart-mcp-server` to use the absolute path: `C:\Program Files\Dart\dart-sdk\bin\dart.exe`.
- Move `cloudrun` and `firebase-mcp-server` into the `mcpServers` object.

## Verification Plan

### Manual Verification
- Verify the JSON is valid using a JSON linter or by simply reading the corrected file.
- Check that all servers are correctly nested under `mcpServers`.
- Suggest the user to restart their MCP client to pick up the changes.
