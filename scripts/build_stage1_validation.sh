#!/usr/bin/env bash
set -euo pipefail

rm -rf _site _extract
mkdir -p _site _extract
unzip -q capture_my_heart_v0_5_1.zip -d _extract
cp -a _extract/capture_my_heart_v0_5_1/. _site/

cp overrides/config.js _site/config.js
cp overrides/feedback.js _site/feedback.js
cp overrides/collection.js _site/collection.js
cp overrides/collection.html _site/collection.html
cp overrides/analytics.js _site/analytics.js
cp overrides/character_masks.js _site/character_masks.js
cp overrides/privacy.html _site/privacy.html
cp overrides/site-info.css _site/site-info.css
cp overrides/info.html _site/info.html
cp overrides/guide.html _site/guide.html
cp overrides/updates.html _site/updates.html
cp overrides/faq.html _site/faq.html
cp overrides/contact.html _site/contact.html
cp overrides/robots.txt _site/robots.txt
cp overrides/sitemap.xml _site/sitemap.xml
cp overrides/ads.txt _site/ads.txt
mkdir -p _site/en
cp -a overrides/en/. _site/en/
cp overrides/sw.js _site/sw.js

mkdir -p _site/assets/bonus
for n in $(seq -w 1 10); do
  src="overrides/assets/stage${n}_service.mp4"
  dst="_site/assets/bonus/stage${n}_service.mp4"
  test -f "$src"
  cp "$src" "$dst"
done

mkdir -p _site/admin
cp -a overrides/admin/. _site/admin/

python overrides/playfeel_patch.py _site
python overrides/mobile_controls_patch.py _site
python overrides/analytics_patch.py _site
python overrides/mobile_layout_patch.py _site
python overrides/adsense_verify_patch.py _site
python overrides/bonus_scene_patch.py _site
python overrides/visual_refresh_patch.py _site
python overrides/age_gate_patch.py _site
python overrides/interactive_tutorial_patch.py _site
python overrides/mobile_ux_v2_patch.py _site
python overrides/mobile_landscape_hud_patch.py _site
python overrides/mobile_viewport_enlarge_patch.py _site
python overrides/feedback_round1_patch.py _site
python overrides/balance_round1_patch.py _site
python overrides/juice_v1_patch.py _site
python overrides/boss_breakout_patch.py _site
python overrides/character_mask_shadow_patch.py _site
python overrides/character_mask_stage1_gate_patch.py _site
python overrides/stage1_emergency_escape_patch.py _site
python overrides/containment_pressure_patch.py _site
python overrides/collection_reward_patch.py _site
python overrides/stage1_rage_v2_patch.py _site
python overrides/service_scene_v2_patch.py _site
python overrides/difficulty_v2_patch.py _site
python overrides/collection_reliability_hotfix_patch.py _site
python overrides/collection_reopen_3d_patch.py _site
python overrides/mobile_rotation_recovery_patch.py _site
python overrides/hud_audio_controls_patch.py _site
python overrides/key_mapping_patch.py _site
python overrides/adsense_content_hub_patch.py _site
python overrides/bilingual_home_patch.py _site
python overrides/bilingual_content_nav_patch.py _site
python overrides/stage1_retention_patch.py _site

zip -q -j _site/assets/cmh-complete-collection.zip \
  _site/assets/images/stage01.webp _site/assets/images/stage02.webp \
  _site/assets/images/stage03.webp _site/assets/images/stage04.webp \
  _site/assets/images/stage05.webp _site/assets/images/stage06.webp \
  _site/assets/images/stage07.webp _site/assets/images/stage08.webp \
  _site/assets/images/stage09.webp _site/assets/images/stage10.webp

rm -rf _site/functions
rm -f _site/wrangler.toml.example
touch _site/.nojekyll

test -f _site/index.html
test -f _site/game.js
test -f _site/analytics.js
test -f _site/styles.css
test -f _site/assets/images/stage01.webp
for n in $(seq -w 1 10); do test -f "_site/assets/bonus/stage${n}_service.mp4"; done

node --check _site/game.js
node --check _site/analytics.js
node overrides/verify_key_mapping.js _site/game.js
node overrides/verify_stage1_retention.js _site/game.js

grep -q "v0.13.8-dev stage1 retention" _site/index.html
grep -q "VERSION: '0.13.8-dev'" _site/config.js
grep -q "cmh-core-v0.13.8-dev" _site/sw.js
grep -q "CLEAR_BANK_V1={enabled:false" _site/game.js
grep -q "stage1_attempt_end" _site/game.js

echo "DEV validation build ready: $(find _site -type f | wc -l) files"
