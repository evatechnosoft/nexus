# Plan: Add Game Development Skills

The goal is to provide the user with relevant game development skills from the central skills repository and integrate them into the project workspace `c:/projects/Antigravity/EvaGames/evario`.

## Proposed Changes

### Project Structure
- [NEW] `.agents/skills` directory to store project-specific skills.

### Skills to be Added
- [x] **game-development**: General principles and routing.
- [x] **game-development/2d-games**: Specific principles for 2D development (sprites, tilemaps, etc.).

## 2D Game Design: "Evario Odyssey" (Mario-Style)
We are building a premium 2D platformer inspired by classic Mario mechanics but with modern, high-end aesthetics.

### Technical Stack
- **Engine**: Vite + Vanilla JS + Canvas API.
- **Physics**: Custom AABB collision system with "Coyote Time" and "Jump Buffering" (from `2d-games` skill).
- **Aesthetics**: Vibrant, neon-accented levels, parallax backgrounds, and smooth character animations.

### Core Gameplay
- **Movement**: Left/Right walking, jumping with variable height.
- **Environment**: Interactive tiles (blocks to hit, platforms to land on).
- **Goal**: Collect digital "Eva-nodes" and reach the end of the stage.

## Implementation Steps
1. [x] Create `.agents/skills` directory and copy skills.
2. [x] Initialize Vite + Vanilla JS project.
3. [x] Character Customization (Sprite, Animation, Glow, Transparency).
4. [x] Initial Sky & Cloud World Implementation.
5. [/] Environment Enhancement:
    - Update sky background to a vibrant blue. <!-- id: 25 -->
    - Generate pixel-art grass/dirt tiles (flat grass top) and blue-ish lava/water tiles (wave-like motion). <!-- id: 21 -->
    - Update `levelMap` to distinguish between floating clouds and ground.
    - Implement wave-like animation logic for lava/water. <!-- id: 26 -->
    - Process new tiles with chroma key for transparency.
6. [/] Asset & UI Refinement:
    - Replace "NODES" with "STARS" in the UI. <!-- id: 27 -->
    - Generate improved 2-frame "stepping and arm swinging" walk animation. <!-- id: 32 -->
    - Generate improved 2-frame glowing blue/white star sprites. <!-- id: 28 -->
    - Implement smooth, continuous ground rendering (no visible seams or stripes). <!-- id: 33 -->
7. [ ] Final polish and verification of all animations. <!-- id: 35 -->

## Verification Plan
### Automated Tests
- `npm run dev` to verify the game loads and the loop runs at 60 FPS.

### Manual Verification
- Verify files in `.agents/skills`.
- Check browser console for any errors during startup.
