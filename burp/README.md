# Burp Suite project template

A Burp project template I reuse for web/API testing: no cookies, no history,
only scope rules, a Logger++ config and an extension list.

## Scope

Regex-based scope with in-scope filtering, static resources (`js`, `css`,
images, fonts) filtered out of the Proxy history to cut noise.

## Logger++

Highlighting and grep rules tuned for object-identifier fields, since most of
what I look for is IDOR and broken access control, not injection:

- `user_id`, `uid`
- `eventId`, `layerId`
- `account_id`, `owner_id`

Logging is limited to Proxy and Repeater traffic.

## Workflow

Repeater-first: duplicate a request as user A, swap the session/token for
user B, diff the responses. No automated scanner is configured here on
purpose — this template is for manual authorization testing.

## Extensions

Only Logger++ ships by default. Add anything else per engagement.

## Before you import this

The template itself has no cookies, tokens or history, but double-check before
sharing a project file from an actual engagement — Burp happily saves
everything you captured in it.
