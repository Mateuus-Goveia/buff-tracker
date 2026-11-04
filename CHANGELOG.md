# Changelog

Notable changes to Buff Tracker are recorded here.

## [0.1.0-beta.2] - 2026-11-04

Second public beta, adding an optional in-game companion overlay and improving buff setup and contact information.

- Add a translucent, always-on-top buff overlay with adjustable opacity, drag positioning, and click-through support.
- Add an About and Contact section with the maintainer's GitHub, LinkedIn, and project email.
- Rename the 22 reminder sound files and give them localized, human-readable names in the sound selector.
- Correct Focus, Iron Body, all Booster skills, Rage, Iron Will, Magic Armor, Meditation, Invincible, Bless, Soul Arrow, and Haste durations using the verified level tables.
- Remove Magic Guard and Dark Sight from timed buff tracking because they do not have fixed durations.
- Keep existing saved buff presets compatible and skip the removed untimed skills when loading them.
- Keep support for older sound names in existing presets.

### Known limitations

- The beta is packaged for Windows; other operating systems are not supported yet.
- The overlay may not appear above games running in exclusive full-screen mode; use windowed or borderless mode.
- Keyboard mode listens for assigned keys while the app is open and does not suppress key presses.
- Update checks only notify and open the GitHub releases page; updates are not downloaded or installed automatically.

## [0.1.0-beta.1] - 2026-11-03

First public beta.

- Track MapleStory Classic buff and consumable timers.
- Support joystick/controller shortcuts and keyboard shortcuts with unique key assignments.
- Provide English and Portuguese interfaces.
- Include 22 reminder sounds and let users choose a sound for each buff.
- Offer PayPal and Pix donation links.
- Provide a portable Windows build and a manual GitHub release check.
- Add unit tests and contributor documentation.

### Known limitations

- The beta is packaged for Windows; other operating systems are not supported yet.
- Keyboard mode listens for assigned keys while the app is open and does not suppress key presses.
- Update checks only notify and open the GitHub releases page; updates are not downloaded or installed automatically.
