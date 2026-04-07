# Hitfile Downloader Plan (via OkDebrid)

Instead of a direct Hitfile download (which has high wait times and CAPTCHAs), we will use `okdebrid.com` to generate a direct link. This process involves navigating through several interstitial "article" pages.

## Proposed Solution
A Puppeteer script that:
1. Navigates to `okdebrid.com`.
2. Inputs the Hitfile URL into the generator.
3. Automatically navigates through the 3-4 interstitial pages (waiting for progress bars to finish).
4. Clicks the final "START DOWNLOAD" button to trigger the file transfer.

## Proposed Changes

### [NEW] [okdebrid_downloader.js](file:///C:/Users/Deacjx/.gemini/antigravity/scratch/scribd-dl/okdebrid_downloader.js)
A Puppeteer script to automate the OkDebrid flow.

### [MODIFY] [download_hitfile.ps1](file:///C:/Users/Deacjx/.gemini/antigravity/scratch/scribd-dl/download_hitfile.ps1)
Update the PowerShell wrapper to use the OkDebrid script.

## Verification Plan
1. Test with the provided Hitfile link: `https://hitfile.net/download/free/MbmVOy3`.
2. Verify that it reaches the final "START DOWNLOAD" state and triggers a download.
