import puppeteer from 'puppeteer';
import path from 'path';

const url = process.argv[2];
if (!url) {
    console.error('Usage: node okdebrid_downloader.js <hitfile_url>');
    process.exit(1);
}

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

(async () => {
    const browser = await puppeteer.launch({
        executablePath: chromePath,
        headless: false, // Set to false to see the process and handle any unexpected issues
        defaultViewport: null,
        args: ['--start-maximized']
    });

    try {
        const page = await browser.newPage();
        console.log('Navigating to OkDebrid...');
        await page.goto('https://okdebrid.com/', { waitUntil: 'networkidle2' });

        console.log(`Inputting link: ${url}`);
        await page.waitForSelector('#links');
        await page.type('#links', url);

        console.log('Generating premium link...');
        await page.click('#generate_prem_links');

        // Wait for the "DOWNLOAD" button to appear on the main page
        await page.waitForFunction(() => {
            const btn = document.querySelector('button.uk-button-primary, a.uk-button-primary');
            return btn && (btn.innerText.includes('DOWNLOAD') || btn.innerText.includes('GET LINK'));
        }, { timeout: 60000 });

        console.log('Clicking first DOWNLOAD button...');
        
        // This button often opens a new tab. We need to catch it.
        const [newPage] = await Promise.all([
            new Promise(resolve => browser.once('targetcreated', target => resolve(target.page()))),
            page.evaluate(() => {
                const btn = Array.from(document.querySelectorAll('button, a')).find(el => el.innerText.includes('DOWNLOAD'));
                btn.click();
            })
        ]);

        if (!newPage) {
            console.error('Failed to capture the new tab.');
            await browser.close();
            return;
        }

        await newPage.bringToFront();
        console.log('Transitioned to interstitial page.');

        // Loop to handle multiple levels of "GET DOWNLOAD" / "GRAB DOWNLOAD"
        let downloadFinished = false;
        let attempts = 0;
        while (!downloadFinished && attempts < 5) {
            attempts++;
            console.log(`Checking for buttons... Attempt ${attempts}`);

            // Wait for progress bar (if any) or the button
            await newPage.waitForFunction(() => {
                const buttons = Array.from(document.querySelectorAll('button, a'));
                return buttons.find(b => 
                    b.innerText.includes('GET DOWNLOAD') || 
                    b.innerText.includes('GRAB DOWNLOAD') || 
                    b.innerText.includes('START DOWNLOAD')
                );
            }, { timeout: 60000 });

            console.log('Found a download-related button.');

            const buttonText = await newPage.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button, a'));
                const btn = buttons.find(b => 
                    b.innerText.includes('GET DOWNLOAD') || 
                    b.innerText.includes('GRAB DOWNLOAD') || 
                    b.innerText.includes('START DOWNLOAD')
                );
                const text = btn.innerText;
                btn.click();
                return text;
            });

            console.log(`Clicked: ${buttonText}`);

            if (buttonText.includes('START DOWNLOAD')) {
                console.log('Final download button clicked! Download should start shortly.');
                downloadFinished = true;
                // Wait a bit to ensure the download triggers
                await new Promise(r => setTimeout(r, 10000));
            } else {
                // Wait for the next page to load or content to change
                await new Promise(r => setTimeout(r, 5000));
                // Sometimes it opens yet ANOTHER tab. Check for that.
                const pages = await browser.pages();
                if (pages.length > 2) {
                    await pages[pages.length - 1].bringToFront();
                }
            }
        }

    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        console.log('Script finished. Closing browser in 30 seconds...');
        await new Promise(r => setTimeout(r, 30000));
        await browser.close();
    }
})();
