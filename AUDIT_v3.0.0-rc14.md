# Bellwether v3.0.0-rc14 Audit — Device & Browser Resilience

## Evidence-first scope
The RC13 frontend was inspected before edits. Existing evidence confirmed responsive breakpoints, coarse-pointer targets, reduced-motion handling, mobile developer-tab scrolling, and keyboard shortcuts. The remaining concrete gaps were modal keyboard focus containment/restoration, safe-area handling, very narrow viewport behavior, and short landscape viewport behavior.

## Changes
- Added shared modal focus trapping for Tab/Shift+Tab.
- Restores focus to the control that opened a modal when it closes.
- Focuses the free-form dialogue textarea when dialogue opens.
- Added safe-area padding for bottom navigation and shell edges.
- Added dynamic viewport-height handling for mobile browser chrome.
- Added narrow-phone and short-landscape fallbacks.
- Preserved coarse-pointer target sizing and reduced-motion contracts.

## Verification boundary
This release certifies source-level device/browser contracts and syntax. It does not claim physical Xbox Edge, iOS Safari, Android Chrome, or controller hardware certification because those target devices were not available in the build environment.
