# Backend rules (project conventions)

## Naming
- **Exists → noun**: `NiftySnapshot`, `niftyConstants`
- **Does something → verb**: `fetchNiftyPayload`, `saveNiftySnapshot`, `getLatestNiftySnapshot`

## Clean views
- Use `@api_view` and keep the view limited to:
  - validate inputs (if any)
  - call 1–2 service functions
  - return `Response`
- Avoid mixing business logic into views.

## Single responsibility utilities
- One file = one job.
- Avoid “god util” functions that do multiple things.

## Exceptions + response shape
- Raise custom exceptions when required.
- Let `REST_FRAMEWORK.EXCEPTION_HANDLER` format errors consistently.

## Logging
- Log **one line per successful snapshot save**.
- Log **one line per failure** with stack trace only for unexpected exceptions.

