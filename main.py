import os
import shutil
import zipfile
import asyncio
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from session_manager import SessionManager
from utils.colors import generate_secondary_color
from utils.validators import validate_phone, validate_email, validate_hex_color
from utils.llm import generate_business_copy

# Import Generators
from generators.logo_generator import generate_logo
from generators.business_card import generate_business_card
from generators.letterhead import generate_letterhead
from generators.ppt_generator import generate_ppt
from generators.price_list import generate_price_list
from generators.social_kit import generate_social_kit
from generators.documents import generate_documents
from generators.email_signature import generate_email_signature
from generators.poster import generate_poster
from generators.website_placeholder import generate_website_placeholder

app = FastAPI(title="Magic Business Platform", version="1.0.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start background cleanup task scheduler
@app.on_event("startup")
async def startup_event():
    async def cleanup_loop():
        while True:
            try:
                # Clean sessions older than 24 hours
                SessionManager.clean_old_sessions(max_age_hours=24)
            except Exception as e:
                print(f"Error in cleanup background task: {e}")
            await asyncio.sleep(3600)  # run every hour
            
    asyncio.create_task(cleanup_loop())

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Serve index.html directly on root
@app.get("/")
async def read_root():
    index_path = os.path.join(config.STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Magic Business Web UI is compiling... Please refresh in a moment.</h1>")

@app.post("/api/generate-all")
async def generate_all(
    business_name: str = Form(...),
    owner_name: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    address: str = Form(""),
    tagline: str = Form(""),
    about: str = Form(""),
    services: str = Form(""),
    brand_color: str = Form("#2563EB"),
    secondary_color: str = Form(""),
    logo: UploadFile = File(None),
    gst_number: str = Form(""),
    social_instagram: str = Form(""),
    social_facebook: str = Form(""),
    assets: str = Form("")
):
    # 1. Clean Inputs & Validate
    try:
        brand_color = validate_hex_color(brand_color)
        if phone:
            phone = validate_phone(phone)
        if email:
            email = validate_email(email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Create output session folder
    session_id = SessionManager.create_session()
    session_dir = SessionManager.get_session_dir(session_id)
    
    # 2. Handle Logo Upload
    logo_path = None
    if logo and logo.filename:
        logo_ext = os.path.splitext(logo.filename)[1]
        temp_logo_path = os.path.join(session_dir, f"uploaded_logo{logo_ext}")
        with open(temp_logo_path, "wb") as f_out:
            shutil.copyfileobj(logo.file, f_out)
        logo_path = temp_logo_path
        
    # 3. Parse services list
    services_list = [s.strip() for s in services.strip().split("\n") if s.strip()]
    
    # 4. Fallback copywriting & Secondary Color Generation
    # If tagline or about is blank, call LLM generator
    tagline_generated = tagline
    about_generated = about
    usps = []
    
    if not tagline or not about:
        tagline_generated, about_generated, usps = generate_business_copy(business_name, services_list)
        
    if not secondary_color:
        secondary_color = generate_secondary_color(brand_color)
        
    # Split list of selected assets to generate
    selected_assets = [a.strip() for a in assets.split(",") if a.strip()]
    if not selected_assets:
        selected_assets = [
            "logo", "business_card", "letterhead", "ppt", "price_list", 
            "social_kit", "quotation", "invoice", "receipt", "email_signature", "poster", "website"
        ]
        
    print(f"Generating assets for session {session_id}. Selection: {selected_assets}")
    
    tasks = {}
    
    # logo generator is a prerequisite for other assets to use the generated logo_primary
    # so we run it first, synchronously or ahead of others, so we have logo_primary.png path!
    logo_results = {}
    logo_primary_path = logo_path
    
    if "logo" in selected_assets or not logo_path:
        # Generate text-based logo if logo not uploaded, or generate variants
        logo_results = generate_logo(business_name, brand_color, session_dir, logo_path)
        logo_primary_path = os.path.join(session_dir, "logo_primary.png")
        
    # Wrapper helper definitions for parallel running
    async def task_business_card():
        return await asyncio.to_thread(
            generate_business_card, business_name, owner_name, phone, email, website, 
            address, tagline_generated, services_list, brand_color, logo_primary_path, session_dir
        )
        
    async def task_letterhead():
        return await asyncio.to_thread(
            generate_letterhead, business_name, phone, email, website, address, 
            gst_number, brand_color, logo_primary_path, session_dir
        )
        
    async def task_ppt():
        desc = about_generated
        return await asyncio.to_thread(
            generate_ppt, business_name, owner_name, phone, email, website, address, 
            tagline_generated, desc, services_list, brand_color, session_dir
        )
        
    async def task_price_list():
        return await asyncio.to_thread(
            generate_price_list, business_name, tagline_generated, phone, email, website, 
            services_list, brand_color, session_dir
        )
        
    async def task_social_kit():
        return await asyncio.to_thread(
            generate_social_kit, business_name, tagline_generated, phone, email, website, 
            services_list, brand_color, logo_primary_path, session_dir
        )
        
    async def task_documents():
        return await asyncio.to_thread(
            generate_documents, business_name, owner_name, phone, email, website, address, 
            gst_number, services_list, brand_color, logo_primary_path, session_dir
        )
        
    async def task_email_signature():
        return await asyncio.to_thread(
            generate_email_signature, business_name, owner_name, phone, email, website, 
            tagline_generated, brand_color, logo_primary_path, session_dir
        )
        
    async def task_poster():
        return await asyncio.to_thread(
            generate_poster, business_name, address, brand_color, logo_primary_path, session_dir
        )
        
    async def task_website():
        return await asyncio.to_thread(
            generate_website_placeholder, business_name, tagline_generated, phone, email, 
            website, address, services_list, brand_color, session_dir
        )
        
    # Queue selected async tasks
    async_tasks = {}
    if "business_card" in selected_assets:
        async_tasks["business_card"] = task_business_card()
    if "letterhead" in selected_assets:
        async_tasks["letterhead"] = task_letterhead()
    if "ppt" in selected_assets:
        async_tasks["ppt"] = task_ppt()
    if "price_list" in selected_assets:
        async_tasks["price_list"] = task_price_list()
    if "social_kit" in selected_assets:
        async_tasks["social_kit"] = task_social_kit()
    if "quotation" in selected_assets or "invoice" in selected_assets or "receipt" in selected_assets:
        async_tasks["documents"] = task_documents()
    if "email_signature" in selected_assets:
        async_tasks["email_signature"] = task_email_signature()
    if "poster" in selected_assets:
        async_tasks["poster"] = task_poster()
    if "website" in selected_assets:
        async_tasks["website"] = task_website()
        
    # Execute selected tasks concurrently
    keys = list(async_tasks.keys())
    results = await asyncio.gather(*[async_tasks[k] for k in keys], return_exceptions=True)
    
    # Check results
    completed_files = {}
    if logo_results:
        completed_files.update(logo_results)
        
    for k, r in zip(keys, results):
        if isinstance(r, Exception):
            print(f"Error executing task '{k}': {r}")
        else:
            completed_files.update(r)
            
    # 5. Pack All files into a ZIP
    zip_filename = "brand_package.zip"
    zip_path = os.path.join(session_dir, zip_filename)
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(session_dir):
                for file in files:
                    if file != zip_filename and not file.startswith("uploaded_logo"):
                        file_path = os.path.join(root, file)
                        # Archive path relative to session_dir
                        arcname = os.path.relpath(file_path, session_dir)
                        zip_file.write(file_path, arcname)
    except Exception as e:
        print(f"Error generating zip package: {e}")
        
    # 6. Format visual output JSON for Dashboard UI
    dashboard_items = []
    
    def add_item(name, download, preview):
        # We ensure download and preview represent filenames which can be retrieved via /api/download/{session_id}/{filename}
        dashboard_items.append({
            "name": name,
            "download_url": f"/api/download/{session_id}/{download}",
            "preview_url": f"/api/download/{session_id}/{preview}" if preview else None
        })
        
    if "logo_primary" in completed_files:
        add_item("Company Logo (Primary)", "logo_primary.png", "logo_primary.png")
        if "logo_white" in completed_files:
            add_item("Company Logo (White Variant)", "logo_white.png", "logo_white.png")
        if "logo_black" in completed_files:
            add_item("Company Logo (Black Variant)", "logo_black.png", "logo_black.png")
            
    if "card_front" in completed_files:
        add_item("Business Card (Front Side)", "card_front.png", "card_front.png")
    if "card_back" in completed_files:
        add_item("Business Card (Back Side)", "card_back.png", "card_back.png")
    if "card_pdf" in completed_files:
        add_item("Business Card (Print Ready PDF)", "business_card.pdf", "card_front.png")
    if "card_digital" in completed_files:
        add_item("Digital Visiting Card (WhatsApp)", "card_digital.png", "card_digital.png")
        
    if "letterhead_pdf" in completed_files:
        add_item("Company Letterhead (A4 PDF)", "letterhead.pdf", "letterhead_preview.png")
        
    if "presentation_pptx" in completed_files:
        add_item("Pitch Deck Presentation (PPTX)", "presentation.pptx", "presentation_preview.png")
        
    if "price_list_pdf" in completed_files:
        add_item("Service Price List (A4 PDF)", "price_list.pdf", "price_list_preview.png")
        
    if "social_instagram" in completed_files:
        add_item("Social Media Banner (Instagram)", "social_instagram.png", "social_instagram.png")
    if "social_facebook" in completed_files:
        add_item("Social Media Banner (Facebook Cover)", "social_facebook.png", "social_facebook.png")
    if "social_whatsapp" in completed_files:
        add_item("Social Media Banner (WhatsApp Profile)", "social_whatsapp.png", "social_whatsapp.png")
        
    if "quotation_pdf" in completed_files:
        add_item("Quotation Template (A4 PDF)", "quotation.pdf", "quotation_preview.png")
    if "invoice_pdf" in completed_files:
        add_item("Invoice Template (A4 PDF)", "invoice.pdf", "invoice_preview.png")
    if "receipt_pdf" in completed_files:
        add_item("Payment Receipt Template (A5 PDF)", "receipt.pdf", "receipt_preview.png")
        
    if "email_signature_html" in completed_files:
        add_item("Email Signature (HTML Template)", "email_signature.html", "email_signature.png")
    if "email_signature_png" in completed_files:
        add_item("Email Signature (PNG Image)", "email_signature.png", "email_signature.png")
        
    if "poster_open" in completed_files:
        add_item("Now Open Poster (PNG)", "poster_open.png", "poster_open.png")
        
    if "website_index" in completed_files:
        # For index.html preview, we can use the signature preview or None
        add_item("Business Placeholder Webpage (HTML)", "index.html", "logo_primary.png")
        
    return JSONResponse({
        "success": True,
        "session_id": session_id,
        "tagline": tagline_generated,
        "about": about_generated,
        "secondary_color": secondary_color,
        "zip_url": f"/api/download-all/{session_id}",
        "items": dashboard_items
    })

# Serve generated files individually
@app.get("/api/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    session_dir = SessionManager.get_session_dir(session_id)
    file_path = os.path.join(session_dir, filename)
    
    # Check traversal bounds
    resolved_path = os.path.realpath(file_path)
    resolved_session_dir = os.path.realpath(session_dir)
    if not resolved_path.startswith(resolved_session_dir):
         raise HTTPException(status_code=403, detail="Access denied.")
         
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested branding file not found.")
        
    return FileResponse(file_path, filename=filename)

# Serve generated ZIP package
@app.get("/api/download-all/{session_id}")
async def download_all(session_id: str):
    session_dir = SessionManager.get_session_dir(session_id)
    zip_path = os.path.join(session_dir, "brand_package.zip")
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP package not found. Try regenerating assets.")
        
    return FileResponse(zip_path, filename="magic_brand_package.zip")

from fastapi.responses import HTMLResponse
