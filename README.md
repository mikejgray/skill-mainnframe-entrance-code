# Finished Booting/Entrance Code

## Summary

Skill to ask for entrance code and speak when MAINNFRAME is ready.

## Description

When MAINNFRAME is started or restarted, this skill will speak a notification to the
user. This speech can be enabled/disabled by intent.

Entrance codes are defined in `settings.json` under `entrancecodes`. The key is the
username and the value is the entrance code. The username is spoken aloud and then
made available to other skills via the skill API.

Incompatible with `ovos-skill-boot-finished.openvoiceos` and `skill-core_ready.neongeckocom`.

## Settings

```json
{
  "__mycroft_skill_firstrun": false,
  "entrance_codes": {
    "Mike": "pineapple"
  }
}
```

## Examples

- "Enable ready notifications."
- "Disable load speech."

## Credits

- [xSquaredLabs](https://xsquaredlabs.com)]

## Category

**Daily**
