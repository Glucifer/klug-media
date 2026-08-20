# Jellyfin Watch Tracking

Klug accepts Jellyfin playback start and stop notifications directly from the
official Jellyfin Webhook plugin. Playback progress notifications should remain
disabled; stop notifications already include the final position and runtime.

## Prerequisites

- Klug must have `KLUG_JELLYFIN_BASE_URL`, `KLUG_JELLYFIN_API_KEY`, and
  `KLUG_API_KEY` configured.
- Run the Jellyfin collection snapshot import before enabling playback delivery.
- Install version 18 or newer of the official Jellyfin Webhook plugin. The
  bundled template uses its `json_encode` helper.

## Webhook destination

Create a **Generic Destination** in Jellyfin with:

- URL: `http://172.20.1.20:8010/api/v1/webhooks/jellyfin/events`
- Notification types: `Playback Start` and `Playback Stop`
- Item type: Videos
- User filter: only users mapped in Klug
- Request header: `Content-Type` = `application/json`
- Request header: `X-API-Key` = the value of `KLUG_API_KEY`
- Template: copy `klug_playback_v1.handlebars`
- Send All Properties: disabled
- Trim whitespace: enabled
- Skip empty message bodies: enabled

Do not put the API key into the template or commit a populated key to this
repository.

## Initial reconciliation and cutover

1. Open **Admin → Jellyfin**, verify the connection, and map the Jellyfin user.
2. Run the collection snapshot import again so current item IDs are mapped.
3. Run a reconciliation dry-run. With no explicit date, the first run examines
   the previous 90 days.
4. Review unmatched items and ambiguous rewatch counts, then run reconciliation.
5. Leave Kodi/Node-RED delivery active for seven days while Jellyfin is verified
   from the primary Kodi client, another Kodi client, and a native Jellyfin client.
6. Filter **Admin → Scrobbler** to Jellyfin and confirm each completed watch is
   created once.
7. Disable Node-RED delivery to Klug. Retain the exported flow for rollback.

Reconciliation can recover the most recent `LastPlayedDate` for an item. It
cannot invent dates for older rewatches represented only by Jellyfin's
`PlayCount`; those are reported for operator review.
