# IDOR Checklist (API)

## Basic checks
- Can I access another user's object by changing ID?
- Is ownership validated on backend?
- Does server return 403 or 404?

## Two-account testing
- User A creates object
- User B tries to read/update/delete it
- Compare responses

## Common mistakes
- Only checking UI restrictions
- Relying on frontend filters
- Missing object-level permission checks

## Notes
- Always verify real impact in UI
- Use minimal PoC
