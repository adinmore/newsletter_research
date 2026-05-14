import asyncio
from playwright.async_api import async_playwright
import pandas as pd

MAX_EMAILS = 600


async def scrape_atomic_mail():
    data = []

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir="C:/Users/amd9m/AppData/Local/Google/Chrome/User Data",
            channel="chrome",
            headless=False
        )
        page = await context.new_page()
        
        #----
        await page.goto("https://atomicmail.io/app/mailbox/69b2f3189ef0cd30fa282542")
        await page.wait_for_selector("._wrapperItem_o62j1_1")

        emails_scraped = 0

        while emails_scraped < MAX_EMAILS:

            email_rows = await page.query_selector_all("_wrapperItem_o62j1_1")
            print(len(email_rows))
'''
            for i in range(len(email_rows)):
                if emails_scraped >= MAX_EMAILS:
                    break

                # Refresh rows (DOM changes after navigation)
                email_rows = await page.query_selector_all("_wrapperItem_o62j1_1")
                row = email_rows[i]

                # -----------------------------
                # CLICK EMAIL
                # -----------------------------
                await row.click()
                await page.wait_for_selector("CSS_SELECTOR_FOR_EMAIL_BODY")

                # -----------------------------
                # EXTRACT DATA
                # -----------------------------
                try:
                    sender = await page.inner_text("CSS_SELECTOR_SENDER")
                except:
                    sender = ""

                try:
                    subject = await page.inner_text("CSS_SELECTOR_SUBJECT")
                except:
                    subject = ""

                try:
                    datetime = await page.inner_text("CSS_SELECTOR_DATETIME")
                except:
                    datetime = ""

                try:
                    body = await page.inner_text("CSS_SELECTOR_BODY")
                except:
                    body = ""

                # Extract links
                links = []
                link_elements = await page.query_selector_all("CSS_SELECTOR_BODY a")
                for link in link_elements:
                    href = await link.get_attribute("href")
                    if href:
                        links.append(href)

                links_str = ", ".join(links)

                data.append({
                    "Sender": sender,
                    "DateTime": datetime,
                    "Subject": subject,
                    "Body": body,
                    "Links": links_str
                })

                emails_scraped += 1
                print(f"Scraped {emails_scraped}")

                # -----------------------------
                # GO BACK TO INBOX
                # -----------------------------
                await page.go_back()
                await page.wait_for_selector("CSS_SELECTOR_FOR_EMAIL_ROWS")

            # -----------------------------
            # NEXT PAGE
            # -----------------------------
            next_button = await page.query_selector("CSS_SELECTOR_NEXT_PAGE")

            if next_button:
                await next_button.click()
                await page.wait_for_load_state("networkidle")
            else:
                break

        await browser.close()

    # -----------------------------
    # SAVE TO EXCEL
    # -----------------------------
    df = pd.DataFrame(data)
    df.to_excel("atomic_mail_export.xlsx", index=False)

    print("Saved to atomic_mail_export.xlsx")

'''
if __name__ == "__main__":
    asyncio.run(scrape_atomic_mail())