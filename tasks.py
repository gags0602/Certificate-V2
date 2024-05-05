from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.Browser.Selenium import Selenium
from RPA.PDF import PDF
import shutil
from pathlib import Path

@task
def order_robots_from_RobotSpareBin():
    browser.configure(slowmo=1000,browser_engine="chrome")
    open_robot_order_website()
    archive_receipts()

    #close_annoying_modal()
    
def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv("orders.csv")
    for order in orders:
        close_annoying_modal()
        print(order)
        fill_the_form(order)

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")
    page.click("text=Show model info")

def fill_the_form(order):
    page = browser.page()
    page.select_option('//select[@id="head"]', str(order["Head"]))
    tempvar = str(order["Body"])
    quoted_variable = f"'{tempvar}'"
    print(quoted_variable)
    print("input[type='radio'][name='body'][value=quoted_variable]")
    page.click(f"input[type='radio'][name='body'][value={quoted_variable}]")
    page.fill('//input[@placeholder="Enter the part number for the legs"]', order["Legs"])
    page.fill('#address',order["Address"])
    page.click('#order')
    while page.query_selector("#head"):
        page.click('#order')
    pdf_location = store_receipt_as_pdf(order)
    screenshot_location = screenshot_robot(order)
    embed_screenshot_to_pdf(pdf_location, screenshot_location)
    page.click('#order-another')

def store_receipt_as_pdf(order):
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, f"output/{order['Order number']}.pdf")
    pdf_document_location = f"output/{order['Order number']}.pdf"
    print(pdf_document_location)
    return pdf_document_location

def screenshot_robot(order):
    page = browser.page()
    section_element = page.locator("#robot-preview-image")
    section_element.screenshot(path=f"output/{order['Order number']}.png")
    screenshot_location = f"output/{order['Order number']}.png"
    print(screenshot_location)
    return screenshot_location

def embed_screenshot_to_pdf(pdf_location, screenshot_location):
    pdf = PDF()
    list_of_files = [
        pdf_location,
        f'{screenshot_location}:align=center',
    ]
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document=pdf_location
    )
def archive_receipts():
    pdfs_dir = Path('output')
    pdf_files = list(pdfs_dir.glob('*.pdf'))
    temp_dir = Path('temp')
    temp_dir.mkdir(exist_ok=True)
    for pdf in pdf_files:
        shutil.copy(pdf, temp_dir)
    shutil.make_archive('output/processed_pdfs', 'zip', temp_dir)
    shutil.rmtree(temp_dir)
    print("PDF files have been zipped successfully.")




    




