# Cricket Manager 2024 - Patch Notes

## Update v1.1 - February 6, 2026


WORLD CUP

- You can now view the full scorecard for any match you play or quick sim during the World Cup. Previously completed matches just showed a greyed out button with no way to see what happened.

- The World Cup Final match now properly appears after you finish both semi-finals. Before this fix, the final was never generated and the tournament would get stuck.

- After playing a match, the game no longer asks you to manually pick who won. The result is now determined automatically in the background.

- Scorecard totals now correctly show the number of wickets fallen. Previously it would display scores like 158/0 even when multiple wickets had fallen.

- Player names in the scorecard are now displayed correctly. They were previously showing up as "Unknown" for every player.

- The World Cup is now only marked as completed once the Final has actually been played. Before, it could incorrectly show as completed after just the semi-finals.


WORLD CUP STATS

- Team names now show up for all players in the Top 20 Batters and Top 20 Bowlers tables. Previously most players had a blank team column.

- Added a Batting Average column to the Top 20 Batters table.

- Added a Bowling Average column to the Top 20 Bowlers table.

- Added a Matches Played column to both the Top 20 Batters and Top 20 Bowlers tables.


FIXTURES

- Added a World Cup button in the fixtures screen. Clicking it takes you directly to the current year's World Cup fixtures without having to manually change the format and tier dropdowns.


GENERAL

- The game now opens in full screen by default so you can see everything without resizing the window.

- Removed the Quick Actions shortcuts from the main dashboard. Only the Generate Fake Database button remains for a cleaner look.


TRAINING

- Changing your managed team in Settings now immediately updates the Training tab. It shows the correct team name and that team's players right away. Previously it was stuck showing India regardless of which team you selected.

- You no longer need to click Save after changing your managed team. The change applies instantly when you select a new team from the dropdown.

- Player traits in the training dialog now display their proper names and descriptions. For example instead of showing raw data, you will now see something like "Golden Arm (Lv. 3)" along with a description of what the trait actually does.


CRASH FIXES

- Fixed a crash that occurred when trying to quick sim or play a match. The game was trying to read match score data that did not exist, causing it to close unexpectedly.
