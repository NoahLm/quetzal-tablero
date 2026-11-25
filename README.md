# Sales Board

A small dashboard of the numbers in Quetzal CRM, for the Tostadora Quetzal demo organization.

It is a single `app.py` (Python standard library only) that serves on `$PORT` and reads the CRM at
`$APP_QUETZAL_CRM_URL`. `momoto.json` declares that it uses the app `quetzal-crm`; until the CRM's owner
allows it, the page says it is waiting for access.
