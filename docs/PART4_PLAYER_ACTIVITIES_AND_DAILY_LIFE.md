# Part 4 — Player Activities and Daily-Life Framework

Part 4 introduces a persistent player-activity substrate and replaces the preliminary one-click garden action with the first deep daily-life vertical slice.

## Gardening vertical slice

The Ashcroft garden now has persistent soil preparation, soil condition, moisture, weeds, three planting plots, seed stock, crop growth, crop health, growth stages, tending, watering, harvesting, produce storage, and gardening skill progression.

Growth occurs through ordinary game-time advancement. Rain contributes moisture; dry time reduces it. Crop growth responds to moisture, seasonal suitability and weed pressure. Neglect can damage crop health. Harvest yield responds to health.

The initial crop catalogue contains radish, lettuce, carrot and broad bean with bounded authored seasonal suitability and growth requirements.

## Compatibility

The old `player_life.garden_work` and `location_state.ashcroft_cottage.garden_progress` fields are retained and updated as compatibility/progression signals so existing story integration and frozen v0.1.0 behavior are not silently severed.

Old saves migrate by adding `player_activities` defaults without removing existing state.

## Scope boundary

Part 4 establishes the activity framework and gardening vertical slice. Full cooking recipes, economic sale prices, seed purchasing, shops and employment belong to later roadmap parts and should consume this state rather than replace it.
