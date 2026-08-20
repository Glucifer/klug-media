# Jellyfin Watch Tracking

Klug accepts Jellyfin playback start and stop notifications directly from the
official Jellyfin Webhook plugin. Playback progress notifications should remain
disabled; stop notifications already include the final position and runtime.

## Prerequisites

- Klug must have `KLUG_JELLYFIN_BASE_URL`, `KLUG_JELLYFIN_API_KEY`, and
  `KLUG_API_KEY` configured.
- Run the repeatable Jellyfin collection snapshot import before enabling
  playback delivery and after significant library changes.
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
`PlayCount`; those are reported for operator review. `PlayCount` is treated as
informational because it is a lifetime counter and can include repeated playback
starts. An `older_rewatch_dates_unavailable` row still imports the latest missing
watch; only the older, undated rewatches are omitted.

## Restore Jellyfin watched flags from Klug

Use **Admin → Jellyfin → Restore Watched Flags From Klug** when Jellyfin user
data has been lost or after rebuilding the server:

1. Refresh the Jellyfin collection snapshot so Klug has current item IDs.
2. Confirm the Klug user is mapped to the intended Jellyfin user.
3. Run **Preview Restore** and review the movie and episode counts.
4. Run a 10-item pilot batch and verify the flags in Jellyfin and Kodi.
5. Increase the batch size and run **Restore Next Batch** until zero items remain.

The restore is intentionally add-only. It selects completed, non-deleted Klug
watches whose media is still present in the current Jellyfin collection, skips
items Jellyfin already marks played, and uses the latest Klug watch timestamp as
Jellyfin's played date. It never marks an item unplayed and does not touch Klug
watches for media absent from Jellyfin. Re-running a batch is safe because each
request reads the current Jellyfin state before choosing its next bounded batch.
