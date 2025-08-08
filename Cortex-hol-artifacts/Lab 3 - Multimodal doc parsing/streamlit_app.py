import streamlit as st
import pandas as pd
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from snowflake.core import Root
# Import python packages
import os
import sys
import json
import shutil
import datetime
import re
import time
import hashlib
from difflib import SequenceMatcher
import tempfile
from textwrap import dedent
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List
from typing import Tuple
import snowflake.snowpark.session as session
# import pdfplumber
# import PyPDF2
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.core import Root
from snowflake.cortex import complete, CompleteOptions
sp_session = get_active_session()

def query_multi_index_search_service(session, my_service, query_text):
    """ENHANCED HYBRID SEARCH: Image + Enriched Text + Raw Text"""
    query_embedding = get_text_embedding_via_image(session, query_text)
    
    resp = my_service.search(
        # Use ONLY multi_index_query, not both query and multi_index_query
        multi_index_query={
            "image_vector": [
                {"vector": query_embedding}],
             "enriched_chunk":[{"text":query_text}],
            "pdf_text":[{"text":query_text}],
            "raw_chunk_text":[{"text":query_text}]},
        
        columns=[
            "ENRICHED_CHUNK",
            "RAW_CHUNK_TEXT",
            "PDF_FILE_NAME",
            "IMAGE_FILE_NAME",
            "ORIGINAL_FILE_NAME",
            "PAGE_NUMBER"
        ],
        limit=1000
    )
    
    return resp.to_json() 

def create_temp_image_from_text(text: str) -> tuple[str, str]:
    query_hash = hashlib.md5(text.strip().lower().encode()).hexdigest()
    image_filename = f"{query_hash}.png"

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    file_path = temp_file.name
    temp_file.close()

    image = Image.new("RGB", (1000, 200), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), text, fill="black", font=font)
    image.save(file_path)

    return file_path, image_filename

def extract_cited_docs_and_pages(text_answer_str):
    cited = {}
    
    # Find the CITED SOURCES section (more robust extraction)
    cited_section_match = re.search(r"CITED SOURCES:\s*(.+?)(?:\n\n|$)", text_answer_str, re.IGNORECASE | re.DOTALL)
    
    if cited_section_match:
        cited_section = cited_section_match.group(1)
        print(f"DEBUG: Found cited section: {cited_section[:200]}...")
        
        # Pattern 1: [document - page X](url) format
        doc_page_pairs = re.findall(r"\[([a-zA-Z0-9._ -]+?)\s*-\s*page\s*(\d+)\]", cited_section)
        for doc, page in doc_page_pairs:
            doc = doc.strip().lower()
            page = page.strip()
            cited.setdefault(doc, set()).add(page)
            print(f"DEBUG: Added citation: {doc} -> page {page}")
        
        # Pattern 2: [document](url) format - fallback for documents without explicit pages
        if not doc_page_pairs:
            doc_links = re.findall(r"\[([a-zA-Z0-9._ -]+?)\]\(", cited_section)
            for doc in doc_links:
                doc_clean = doc.strip().lower()
                cited.setdefault(doc_clean, set()).add("*")  # Wildcard for any page
                print(f"DEBUG: Added wildcard citation: {doc_clean} -> *")
    else:
        print("DEBUG: No CITED SOURCES section found in text")
    
    print(f"DEBUG: Final extracted citations: {cited}")
    return cited

def extract_page_number(image_file_name: str) -> str:
    match = re.search(r'_page_(\d+)\.png$', image_file_name)
    return match.group(1) if match else "N/A"

def file_exists_in_stage(session, stage_name: str, file_path: str) -> bool:
    result = session.sql(f"list @{stage_name}/{file_path}").collect()
    return bool(result)

def fuzzy_match(a, b, threshold=0.6):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

def upload_file_to_stage(session, local_path: str, stage_name: str, dest_file_name: str):
    temp_dir = tempfile.gettempdir()
    temp_named_path = os.path.join(temp_dir, dest_file_name)

    os.makedirs(os.path.dirname(temp_named_path), exist_ok=True)
    shutil.copyfile(local_path, temp_named_path)

    try:
        result = session.file.put(
            temp_named_path,
            f"@{stage_name}/queries",
            overwrite=True,
            auto_compress=False
        )
        
    finally:
        os.remove(temp_named_path)

def get_text_embedding_via_image(
    session, 
    text: str, 
    stage_name="@cortex_search_tutorial_db.public.doc_repo"
):
    temp_path, image_filename = create_temp_image_from_text(text)
    stage_subpath = f"queries/{image_filename}"

    try:
        if not file_exists_in_stage(session, stage_name.lstrip("@"), stage_subpath):
            upload_file_to_stage(session, temp_path, stage_name.lstrip("@"), stage_subpath)
            
        query = f"""
            select 
                AI_EMBED(
                    'voyage-multimodal-3', 
                    '{stage_name}+{stage_subpath.lstrip('/')}'
                )
        """
        embedding = session.sql(query).collect()[0][0]
    finally:
        os.remove(temp_path)

    return embedding

def resolve_async_job(job):
    try:
        row = job.result()[0].asDict()
        return {
            "RESULT": row["RESULT"],
            "ORIGINAL_FILE_NAME": row["ORIGINAL_FILE_NAME"],
            "IMAGE_FILE_NAME": row["IMAGE_FILE_NAME"],
            "PRESIGNED_URL": row.get("PRESIGNED_URL", "#")
        }
    except Exception as e:
        return {
            "RESULT": f"Error: {e}",
            "ORIGINAL_FILE_NAME": None,
            "IMAGE_FILE_NAME": None,
            "PRESIGNED_URL": "#"
        }

def rephrase_for_search(question):
    return question.strip().lower()

def filter_by_confidence(responses, threshold=0.5):
    filtered = []
    for item in responses:
        match = re.search(r"CONFIDENCE:\s*([0-9.]+)", item["RESULT"], re.IGNORECASE)
        score = float(match.group(1)) if match else 0.0
        if score >= threshold:
            filtered.append(item)
    return filtered

def sql_escape(value):
    return str(value).replace("'", "''") if value is not None else ""

def run_model(model_name, llm_prompt, session, temperature, max_tokens, top_p, guardrails, stream):
    return complete(
        model=model_name,
        prompt=[{"role": "user", "content": llm_prompt}],
        session=session,
        options=CompleteOptions(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            guardrails=guardrails
        ),
        stream=stream
    )

def ai_complete_on_text(session, question, retrieved_chunks):
    seen = set()
    enriched_context_blocks = []

    for chunk in retrieved_chunks:
        enriched_chunk = chunk["ENRICHED_CHUNK"]
        original_file = chunk.get("ORIGINAL_FILE_NAME")
        image_file = chunk.get("IMAGE_FILE_NAME")

        if not image_file or not original_file:
            continue

        key = (original_file, image_file, enriched_chunk)
        if key in seen:
            continue
        seen.add(key)

        # Generate presigned URL
        presigned_url = session.sql(
            f"SELECT GET_PRESIGNED_URL(@cortex_search_tutorial_db.public.doc_repo, '{sql_escape(image_file)}')"
        ).collect()[0][0]

        # Format for the model
        block = dedent(f"""
        ---
        📄 **Source**: [{original_file}]({presigned_url})
        📜 **Extracted Content**:
        {enriched_chunk}
        """).strip()

        enriched_context_blocks.append(block)

    if not enriched_context_blocks:
        return {"result": "No usable context.", "metadata": {}}

    full_context = "\n\n".join(enriched_context_blocks)

    prompt = dedent(f"""
    You are an expert analyst of the 2023 Investment Company Institute (ICI) Fact Book, a comprehensive 
    statistical compendium containing precise financial data about US and global investment companies.

    ## 2023 ICI FACT BOOK SPECIFIC INTELLIGENCE:

    ### Known Data Context:
    - Total registered investment company assets: ~$27+ trillion as of year-end 2023
    - Breakdown by: Mutual Funds (~$20+ trillion), ETFs (~$6+ trillion), Closed-End (~$200+ billion)
    - Major asset classes: Equity (domestic/international), Fixed Income, Money Market, Hybrid
    - Key trend timeframes: 2019-2023 (5-year), 2014-2023 (10-year)

    ### Critical Terminology Precision:
    - "Net assets" = Assets minus liabilities (standard ICI metric)
    - "Total net assets" = Sum across all fund types unless qualified
    - "Asset allocation" = Investment portfolio composition by asset class
    - "Fund assets" = Assets within specific fund type only
    - "Investment company assets" = All registered funds combined

    ## ICI FACT BOOK DATA ARCHITECTURE:
    
    ### Asset Classification Hierarchy:
    - **LEVEL 1 - Asset Classes**: Equity, Fixed Income, Money Market, Hybrid/Balanced
    - **LEVEL 2 - Geographic Scope**: Domestic, International, Global, Regional
    - **LEVEL 3 - Investment Vehicles**: Mutual Funds, ETFs, Closed-End Funds
    - **LEVEL 4 - Investment Objectives**: Growth, Value, Blend, Sector-Specific, Target-Date
    
    ### Data Presentation Standards:
    - **Net Assets**: Always in billions of dollars unless specified otherwise
    - **Percentages**: Typically represent share of total within category
    - **Time Periods**: Year-end data (December 31) unless noted as quarterly
    - **Geographic Coverage**: US data unless explicitly marked as "Worldwide"
    - **Fund Universe**: All registered investment companies unless subset specified
    
    ### Visual Data Types in Context:
    - **Figure Tables**: Numerical data in structured rows/columns with precise values
    - **Bar Charts**: Year-over-year comparisons, often 5-10 year timeframes  
    - **Pie Charts**: Percentage breakdowns that sum to 100%
    - **Line Graphs**: Trend analysis over multiple years
    - **Flow Charts**: Net flows (inflows minus outflows) in billions

    ## PRECISION GUARDRAILS:

    ### Red Flag Validation Checks:
    1. **Scale Reasonableness**: US mutual fund assets should be $15-25 trillion range
    2. **Percentage Validation**: Asset allocation percentages must sum to ~100%
    3. **Temporal Consistency**: 2023 data should show logical progression from 2022
    4. **Geographic Logic**: US domestic equity typically 40-60% of total equity assets
    5. **Fund Type Ratios**: Mutual funds typically 3-4x larger than ETF assets

    ## CRITICAL INTERPRETATION RULES:
    
    ### Asset Allocation Questions:
    - "Net investments by asset class" = TOP-LEVEL asset allocation across equity/fixed income/money market/hybrid
    - "Total net assets" = Sum across ALL investment company types (mutual funds + ETFs + closed-end)
    - "Asset allocation" WITHOUT qualifiers = Comprehensive breakdown across all major categories
    - "Fund assets" WITH qualifiers = Specific to mentioned fund type only
    
    ### Temporal Context:
    - Always specify data year (2023, 2022, etc.)
    - Note if data is year-end vs. quarterly vs. cumulative
    - Multi-year questions require trend analysis across time periods
    
    ### Scale and Scope Precision:
    - Billions vs. trillions notation matters
    - US-only vs. global data distinction is critical
    - Registered vs. unregistered investment companies
    - Retail vs. institutional share classes

    ## INTELLIGENT QUESTION ROUTING:

    ### Question Pattern Analysis:
    - **Allocation Questions** ("by asset class", "breakdown", "distribution")
      → Expect percentage outputs from comprehensive data tables
    - **Trend Questions** ("growth", "change", "over time")  
      → Expect directional analysis from time series data
    - **Comparison Questions** ("vs", "compared to", "relative")
      → Expect relative metrics from comparative charts
    - **Scale Questions** ("total", "size", "how much")
      → Expect absolute values from aggregate statistics

    ## ENHANCED ACCURACY PROTOCOLS:
    
    ### Data Validation Checklist:
    1. **Scope Match**: Does data scope exactly match question parameters?
    2. **Time Alignment**: Is the time period precisely what was asked?
    3. **Scale Verification**: Are units (billions/percentages) correctly interpreted?
    4. **Completeness Check**: For "total" questions, is all relevant data included?
    5. **Category Precision**: Are asset classes vs. fund types vs. objectives correctly distinguished?
    
    ### Common Precision Errors to Avoid:
    - Confusing "mutual fund equity assets" with "total equity assets across all vehicles"
    - Mixing domestic and international data when only one was requested
    - Using partial year data when year-end was implied
    - Conflating investment objectives with asset classes
    - Missing geographic or vehicle-type qualifiers

    ## CONFIDENCE SCORING PRECISION:

    ### Confidence Level Guidelines:
    - **1.0**: Direct table lookup with exact match to question parameters
    - **0.9**: Clear chart data with minor interpolation required
    - **0.8**: Multiple consistent sources supporting same conclusion
    - **0.7**: Single good source but some scope mismatch (e.g., 2022 vs 2023 data)
    - **0.6**: Partial data requiring reasonable inference
    - **0.5**: Limited data with significant uncertainty
    - **<0.5**: Insufficient data to answer question reliably

    ### Confidence Reduction Triggers:
    - Data from different time periods than requested (-0.1 to -0.2)
    - Geographic scope mismatch (US vs global) (-0.2)
    - Fund type scope mismatch (specific vs total) (-0.1 to -0.3)
    - Conflicting data between sources (-0.3 to -0.5)
    
    ---
    
    ## QUESTION ANALYSIS:
    **User Question**: {question.strip()}
    
    **Question Type Identification**:
    - Asset allocation breakdown? Geographic analysis? Fund flow trends? Performance comparison?
    - Time-specific or trend analysis? Single category or comprehensive view?
    - Absolute values or relative percentages? Current state or historical change?
    
    ## CONTEXT BLOCKS:
    {full_context}
    
    ---
    
    ## REQUIRED OUTPUT FORMAT:
    
    DIRECT ANSWER: [Precise numerical answer with units, time period, and scope clearly specified]
    
    CONFIDENCE: [0.0-1.0 following guidelines above, with specific reasoning for score]
    
    JUSTIFICATION: [Explanation referencing specific ICI data points, noting any limitations, scope restrictions, or validation checks applied]
    
    CITED SOURCES: [2023-factbook - page X](presigned_url) [2023-factbook - page Y](presigned_url)
    
    ## CRITICAL SUCCESS METRICS:
    - Numerical precision to appropriate decimal places
    - Explicit time period and geographic scope
    - Clear distinction between asset classes, fund types, and investment objectives  
    - Comprehensive coverage when "total" or "all" is requested
    - Acknowledgment of data limitations or gaps if present
    - Applied validation checks against known ICI data patterns
    
    Your Response:
    """)

    result = complete(
        model="claude-4-sonnet",
        prompt=[{"role": "user", "content": prompt}],
        session=session,
        options=CompleteOptions(
            temperature=0.05,  # Very low for maximum precision
            max_tokens=1500,   # Conservative to avoid token limit issues
            top_p=0.9,
            guardrails=False
        ),
        stream=False
    )

    return {
        "result": "".join(result),
        "metadata": {
            "source": "TEXT",
            "num_chunks": len(retrieved_chunks)
        },
        "prompt": prompt
    }
    
def ai_complete_on_image_async(session, question, item, text_answer):
    image_file_name = item["IMAGE_FILE_NAME"]
    original_file_name = item.get("ORIGINAL_FILE_NAME", "")
    page_number = item.get("PAGE_NUMBER", "")

    # Escape for SQL
    image_file_escaped = sql_escape(image_file_name)
    original_file_escaped = sql_escape(original_file_name)
    document_metadata_escaped = sql_escape(original_file_name)
    page_metadata_escaped = sql_escape(str(page_number))
    answer_snippet_escaped = sql_escape(text_answer["result"][:2000])

    prompt = dedent(f"""
    You are an expert visual analyst specializing in ICI Investment Company Fact Book financial charts, 
    tables, and infographics. Your role is to extract precise data from visual elements and validate 
    text-based answers against actual document imagery.

    ## ICI VISUAL DATA EXPERTISE:

    ### Chart Type Recognition & Analysis:
    - **Statistical Tables**: Multi-column layouts with headers, often showing year-over-year data
      → Extract: Exact values, time periods, row/column labels, footnotes
    - **Horizontal Bar Charts**: Category comparisons or time series
      → Extract: Scale values, category labels, time periods, data values
    - **Pie Charts**: Percentage breakdowns of total allocation
      → Extract: Segment percentages, labels, total represented, time period
    - **Line Graphs**: Trend analysis over multiple years
      → Extract: Axis labels, scale, trend direction, specific data points
    - **Infographics**: Key statistics with visual emphasis
      → Extract: Highlighted numbers, comparative ratios, summary statistics

    ### ICI-Specific Visual Patterns:
    - **Asset Allocation Pies**: Typically show equity/fixed income/money market/hybrid splits
    - **Flow Charts**: Show net flows with positive/negative indicators, usually in billions
    - **Time Series**: Usually 5-10 year timeframes ending in current year (2023)
    - **Geographic Breakdowns**: US vs. International or regional distributions
    - **Fund Type Comparisons**: Mutual funds vs. ETFs vs. closed-end funds

    ### ADVANCED VISUAL INTELLIGENCE:

    #### ICI Chart Pattern Recognition:
    - **Figure Numbers**: ICI uses "Figure X.X" numbering - extract for precise citation
    - **Table Headers**: Often multi-level headers (Year, Category, Subcategory)
    - **Footnote Symbols**: *, †, ‡ indicate important qualifiers - ALWAYS check
    - **Color Coding**: Consistent colors for fund types across charts
    - **Scale Breaks**: Watch for axis breaks that might distort visual interpretation

    #### Visual Data Extraction Hierarchy:
    1. **Primary Data**: Main chart/table values (highest priority)
    2. **Footnotes**: Critical context and definitions  
    3. **Source Lines**: Data collection methodology and timing
    4. **Axis Labels**: Units, time periods, geographic scope
    5. **Legend Information**: Category definitions and color coding

    ### Visual Data Extraction Protocol:
    1. **Chart Title & Context**: What is being measured, time period, scope
    2. **Axis Labels & Scales**: Units (billions, percentages), time periods, categories
    3. **Data Values**: Precise numbers, percentages, trends
    4. **Footnotes & Qualifiers**: Important context about data scope or methodology
    5. **Visual Emphasis**: What data points are highlighted or emphasized

    ## VALIDATION TASK:

    **Original Question**: {question.strip()}
    
    **Text Answer Being Validated**:
    {text_answer["result"]}
    
    **Image Source**: Document: `{original_file_name}`, Page: {page_number}

    ## SYSTEMATIC VISUAL ANALYSIS:

    ### Step 1: Image Content Identification
    - What type of visual element is this? (table, chart, infographic, mixed)
    - What is the primary data being presented?
    - What time period and scope does it cover?
    - Are there Figure numbers or Table numbers for precise citation?
    
    ### Step 2: Precise Data Extraction
    - Extract all relevant numerical values visible in the image
    - Note units (billions, percentages, etc.), time periods, and categorical labels
    - Identify any footnotes, symbols, or qualifiers
    - Check for multi-level headers or complex data structures
    
    ### Step 3: Answer Validation
    - Compare text answer values with visual data point by point
    - Check time periods, scope, and units match exactly
    - Verify completeness - is any relevant visual data missing from text answer?
    - Assess if text answer scope aligns with visual data scope
    
    ### Step 4: Accuracy Assessment
    - Are there numerical discrepancies between text and visual?
    - Is the text answer scope too narrow or too broad for the visual data?
    - Does the text answer properly interpret the visual context and footnotes?
    - Are there additional insights in the visual that enhance the answer?

    ## ENHANCED VALIDATION CRITERIA:

    ### Numerical Precision:
    - Values match exactly or within reasonable rounding (±0.1% for percentages)
    - Units (billions/percentages/ratios) correctly interpreted
    - Time periods precisely aligned with what's shown
    - Scale factors (thousands, millions, billions) properly applied
    
    ### Scope Alignment:
    - Geographic scope (US vs. global) correctly identified from visual labels
    - Fund type coverage (all vs. specific) properly interpreted from chart context
    - Asset class vs. fund type distinction maintained per visual categorization
    - Time period coverage matches visual data timeframe
    
    ### Completeness Assessment:
    - All relevant visual data incorporated into assessment
    - No cherry-picking of convenient data points
    - Comprehensive answer when visual shows comprehensive data
    - Footnotes and qualifiers properly considered

    ### ICI-Specific Validation:
    - Asset allocation percentages sum to 100% (±1% for rounding)
    - Fund type ratios align with known ICI patterns (MF > ETF > CEF)
    - Time series show logical progression year-over-year
    - Geographic splits align with US investment patterns

    ## REQUIRED OUTPUT FORMAT:

    CRITIQUE_RESULT: [CONFIRMED/REQUIRES_CORRECTION/NEEDS_ENHANCEMENT] - [Brief assessment with specific reasoning]
    
    VISUAL_DATA_EXTRACTED: [Specific values, percentages, trends visible in image with exact figures, units, and time periods]
    
    ACCURACY_VALIDATION: [Detailed point-by-point comparison of text answer vs. visual data with specific discrepancies noted]
    
    SCOPE_ASSESSMENT: [Whether text answer scope matches visual data scope - time period, geography, fund types, completeness]
    
    FOOTNOTE_ANALYSIS: [Any footnotes, symbols, or qualifiers visible that affect interpretation]
    
    MISSING_INSIGHTS: [Any relevant data visible in image but not captured in text answer]
    
    CORRECTED_ANSWER: [If corrections needed, provide precise corrected answer based on visual data with exact values and proper context]
    
    CONFIDENCE_IN_VALIDATION: [0.0-1.0 based on clarity of visual data, completeness of extraction, and certainty of assessment]
    
    ## CRITICAL VALIDATION FOCUS:
    - ICI Fact Book visual elements are authoritative source of truth
    - Extract exact numerical values, not approximations
    - Consider footnotes and qualifiers as critical context
    - Distinguish between individual data points and totals/summaries
    - Maintain precision in temporal and geographic scope
    - Apply ICI-specific knowledge of data patterns and relationships
    
    Analysis:
    """)

    prompt_escaped = prompt.replace("'", "\\'")

    df = session.sql(f"""
        select 
            '{original_file_escaped}' as original_file_name,
            '{image_file_escaped}' as image_file_name,
            '{document_metadata_escaped}' as document_metadata,
            '{page_metadata_escaped}' as page_metadata,
            get_presigned_url('@CORTEX_SEARCH_TUTORIAL_DB.public.doc_repo', '{image_file_escaped}') as presigned_url,
            ai_complete(
                'claude-4-sonnet',
                '{prompt_escaped}',
                to_file('@CORTEX_SEARCH_TUTORIAL_DB.public.doc_repo', '{image_file_escaped}'),
                object_construct('temperature', 0.1, 'top_p', 0.9, 'max_tokens', 2500, 'guardrails', FALSE)
            ) as result
    """)
    return df.collect_nowait()

def synthesise_all_answers(session, question, text_answer_dict, image_answer_dicts):
    text_result = text_answer_dict["result"]
    text_meta = text_answer_dict.get("metadata", {})

    image_sections = []
    for img in image_answer_dicts:
        presigned_link = img.get("PRESIGNED_URL", "#")
        section = dedent(f"""
        --- 
        📄 **Source**: [{img["ORIGINAL_FILE_NAME"]}]({presigned_link})
        🖼️ Image File: `{img["IMAGE_FILE_NAME"]}`

        📘 Page Metadata:
        {img.get("PAGE_METADATA", "N/A")}

        📚 Document Metadata:
        {img.get("DOCUMENT_METADATA", "N/A")}

        📌 Visual Validation Results:
        {img["RESULT"]}
        """)
        image_sections.append(section.strip())

    image_critique_block = "\n\n".join(image_sections)

    prompt = dedent(f"""
    You are synthesizing the definitive answer to a question about 2023 ICI Investment Company Fact Book data, 
    combining text-based analysis with visual validation from actual document pages to create the most 
    accurate and authoritative response possible.

    ## SYNTHESIS OBJECTIVE:
    Create the most accurate, complete, and precise answer by integrating:
    1. Text-based analysis from enriched document chunks
    2. Visual validation from actual ICI Fact Book page images
    3. Cross-validation between multiple data sources
    4. Application of ICI-specific knowledge and data patterns

    ## USER QUESTION:
    {question}

    ## TEXT-BASED ANALYSIS:
    {text_result}

    ## VISUAL VALIDATION RESULTS:
    {image_critique_block}

    ## SYNTHESIS REQUIREMENTS:

    ### Accuracy Priority Hierarchy:
    1. **Visual data from ICI pages** (authoritative when clear and relevant)
    2. **Text analysis validated by visuals** (high confidence)
    3. **Consistent text analysis across sources** (good confidence)
    4. **Single source text analysis** (moderate confidence)
    5. **Inference from partial data** (low confidence - note limitations)

    ### Conflict Resolution Protocol:
    - If visual contradicts text: Prioritize visual data (ICI pages are source of truth)
    - If multiple visuals conflict: Note discrepancy and use most comprehensive source
    - If visual unclear: Rely on text analysis but note visual limitation
    - If both uncertain: Provide best available answer with clear confidence qualifier

    ### Precision Standards for ICI Data:
    - Maintain exact numerical values from authoritative sources
    - Specify time periods (year-end 2023, Q4 2023, etc.)
    - Include geographic scope (US, global, international)
    - Note data universe (all investment companies, specific fund types)
    - Use proper ICI terminology and category definitions
    - Include appropriate units (billions of dollars, percentages, basis points)

    ### Completeness Assessment:
    - Ensure answer fully addresses the question scope
    - Include all relevant data when comprehensive breakdown requested
    - Distinguish between asset classes, fund types, and investment objectives
    - Note if partial data or if additional context would enhance understanding
    - Address both quantitative data and qualitative insights when relevant

    ## ICI-SPECIFIC SYNTHESIS INTELLIGENCE:

    ### Data Validation Against Known Patterns:
    - Total investment company assets: ~$27+ trillion (2023)
    - Mutual funds should dominate (70-75% of total)
    - ETFs growing but still smaller (20-25% of total)
    - Closed-end funds smallest segment (1-2% of total)
    - Equity typically largest asset class (50-60%)
    - Fixed income second largest (25-35%)
    - Money market varies with market conditions (5-15%)

    ### Synthesis Quality Checks:
    - Do totals add up appropriately?
    - Are percentages reasonable within ICI context?
    - Does temporal data show logical progression?
    - Are geographic splits consistent with US investment patterns?
    - Do fund type ratios align with market structure?

    ## FINAL ANSWER REQUIREMENTS:

    **Tone**: Professional, authoritative, precise (suitable for financial analysis)
    **Structure**: 
    1. Direct answer to question with key figures
    2. Additional context and breakdowns as relevant
    3. Time period and scope qualifiers
    4. Any important limitations or notes

    **Precision**: 
    - Exact figures with proper units and context
    - Appropriate decimal places (typically 1 decimal for percentages)
    - Clear temporal and geographic qualifiers
    - Proper distinction between categories

    **Sources**: Clean citation format with working hyperlinks to actual pages

    ## ENHANCED SYNTHESIS PROTOCOL:

    ### Integration Strategy:
    1. **Start with most authoritative data** (visual validation when available)
    2. **Layer in supporting context** from text analysis
    3. **Cross-reference for consistency** across all sources
    4. **Apply ICI knowledge** for reasonableness checks
    5. **Note any limitations** or gaps in available data

    ### Output Optimization:
    - Lead with direct numerical answer when possible
    - Provide context that enhances understanding
    - Use proper financial terminology
    - Maintain professional tone suitable for investment industry
    - Include actionable insights when relevant

    ## OUTPUT FORMAT:

    [Provide comprehensive, accurate answer based on synthesis of all available data, leading with direct response to question, followed by relevant context and qualifiers]

    **Cited Sources**:
    - [2023-factbook - page X](url)
    - [2023-factbook - page Y](url)

    ## SYNTHESIS SUCCESS CRITERIA:
    - Numerical accuracy verified against visual sources when available
    - Scope precisely matches question parameters
    - Time periods and geographic context clearly specified
    - Comprehensive coverage when broad questions asked
    - Professional presentation suitable for financial analysis
    - Confidence level appropriately calibrated to data quality
    - ICI-specific patterns and knowledge properly applied

    Final Answer:
    """)

    result = complete(
        model="claude-4-sonnet",
        prompt=prompt,
        session=session,
        options=CompleteOptions(
            temperature=0.1,  # Low for precise synthesis
            max_tokens=1500,  # Conservative to avoid token limits
            top_p=0.9,
            guardrails=False
        ),
        stream=False
    )

    return "".join(result)

import re

def smart_chunk_selection(chunks, question, max_chunks=10):
    """ENHANCED HYBRID CHUNK SELECTION: Balances enriched context with raw text precision"""
    
    # ICI-specific high-value keywords with enhanced weighting
    ici_keywords = {
        'asset': 3, 'allocation': 3, 'class': 2, 'total': 3, 'net': 2,
        'equity': 2, 'fixed': 2, 'income': 2, 'money': 2, 'market': 2,
        'mutual': 2, 'fund': 2, 'etf': 2, 'exchange': 2, 'traded': 2,
        'billion': 3, 'trillion': 3, 'percentage': 2, 'breakdown': 3,
        'domestic': 2, 'international': 2, 'flow': 2, 'investment': 1,
        'company': 1, 'registered': 2, '2023': 3, '2022': 2
    }
    
    question_words = [word.lower().strip('.,!?') for word in question.split()]
    
    scored_chunks = []
    for chunk in chunks:
        # HYBRID SCORING: Consider both enriched and raw content
        enriched_text = chunk.get("ENRICHED_CHUNK", "").lower()
        raw_text = chunk.get("RAW_CHUNK_TEXT", "").lower()
        
        # Base relevance from question keywords in BOTH texts
        enriched_base = sum(3 for word in question_words if len(word) > 3 and word in enriched_text)
        raw_base = sum(4 for word in question_words if len(word) > 3 and word in raw_text)  # Higher weight for exact matches
        
        # ICI-specific scoring for both texts
        enriched_ici = sum(weight for term, weight in ici_keywords.items() if term in enriched_text)
        raw_ici = sum(weight * 1.2 for term, weight in ici_keywords.items() if term in raw_text)  # Slight boost for raw
        
        # Numerical data bonuses (more likely in raw text for exact figures)
        enriched_numerical = len(re.findall(r'\b\d+\.?\d*\b', enriched_text)) * 0.3
        raw_numerical = len(re.findall(r'\b\d+\.?\d*\b', raw_text)) * 0.8  # Higher weight for raw numbers
        
        # Percentage bonuses
        enriched_percentage = len(re.findall(r'\b\d+\.?\d*%', enriched_text)) * 0.5
        raw_percentage = len(re.findall(r'\b\d+\.?\d*%', raw_text)) * 1.2  # Raw percentages more precise
        
        # Year bonuses for both
        enriched_year = 1 if '2023' in enriched_text else (0.5 if '2022' in enriched_text else 0)
        raw_year = 2 if '2023' in raw_text else (1 if '2022' in raw_text else 0)
        
        # QUALITY BONUSES:
        # Enriched chunks with visual context get bonus
        visual_bonus = 1 if 'visual context' in enriched_text or 'chart' in enriched_text or 'table' in enriched_text else 0
        
        # Raw chunks with exact financial terms get bonus
        financial_bonus = 1 if any(term in raw_text for term in ['$', 'billion', 'trillion', 'assets', 'net']) else 0
        
        # HYBRID TOTAL SCORE
        total_score = (
            enriched_base + raw_base +
            enriched_ici + raw_ici +
            enriched_numerical + raw_numerical +
            enriched_percentage + raw_percentage +
            enriched_year + raw_year +
            visual_bonus + financial_bonus
        )
        
        scored_chunks.append((total_score, chunk))
    
    # Sort by score and take top chunks
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # BALANCED SELECTION: Ensure mix of high-context and high-precision chunks
    selected_chunks = []
    enriched_heavy = 0
    raw_heavy = 0
    
    for score, chunk in scored_chunks[:max_chunks * 2]:  # Consider more candidates
        if len(selected_chunks) >= max_chunks:
            break
            
        enriched_text = chunk.get("ENRICHED_CHUNK", "")
        raw_text = chunk.get("RAW_CHUNK_TEXT", "")
        
        # Determine if chunk is enriched-heavy or raw-heavy based on content length/richness
        is_enriched_heavy = len(enriched_text) > len(raw_text) * 2
        is_raw_heavy = len(raw_text) > 100 and any(char.isdigit() for char in raw_text)
        
        # Balance selection
        if is_enriched_heavy and enriched_heavy < max_chunks * 0.6:  # Up to 60% enriched
            selected_chunks.append(chunk)
            enriched_heavy += 1
        elif is_raw_heavy and raw_heavy < max_chunks * 0.5:  # Up to 50% raw-focused
            selected_chunks.append(chunk)
            raw_heavy += 1
        elif len(selected_chunks) < max_chunks:  # Fill remaining slots
            selected_chunks.append(chunk)
    
    return selected_chunks 

# ========================================
# STREAMLIT APPLICATION LOGIC
# ========================================

st.title("🏦 Financial Document AI Assistant")

# Initialize session state for all data persistence
if 'custom_results' not in st.session_state:
    st.session_state.custom_results = {}
if 'main_question_processed' not in st.session_state:
    st.session_state.main_question_processed = False
if 'main_results' not in st.session_state:
    st.session_state.main_results = {}

# Sidebar settings
with st.sidebar:
    st.markdown("## ⚙️ Performance Settings")
    st.markdown("**Image Analysis:**")
    MAX_IMAGES_TO_ANALYZE = st.slider("Max Images to Analyze", 1, 20, 8)
    st.write(f"Currently analyzing top {MAX_IMAGES_TO_ANALYZE} images")
    
    if st.button("🔄 Reset All"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# User question input
user_question = st.text_input(
    "💭 Ask a question about financial documents:",
    placeholder="e.g., What are the trends in mutual fund assets?"
)

# Add submit button
col1, col2 = st.columns([3, 1])
with col2:
    submit_clicked = st.button("🔍 Ask Question", type="primary")

# ========================================
# MAIN QUESTION PROCESSING (ISOLATED)
# ========================================

if user_question and submit_clicked:
    # Process the main question and store results
    with st.spinner("🔍 Processing your question..."):
        start_time = time.time()
        
        # Step 1: Search
        st.write("🔍 Step 1 of 7: Searching vector database...")
        root = Root(sp_session)
        search_service = (root
            .databases["CORTEX_SEARCH_TUTORIAL_DB"]
            .schemas["PUBLIC"]
            .cortex_search_services["DOCS_SEARCH_SERVICE"]
        )
        search_results = query_multi_index_search_service(sp_session, search_service, user_question)
        
        # Parse JSON string to Python object if needed
        if isinstance(search_results, str):
            search_results = json.loads(search_results)
        
        # Extract actual results from nested structure
        if isinstance(search_results, dict) and 'results' in search_results:
            search_results = search_results['results']
        elif isinstance(search_results, dict) and 'data' in search_results:
            search_results = search_results['data']
        
        # Step 2: Smart chunk selection
        st.write("🧠 Step 2 of 7: Smart chunk selection...")
        deduped_results = smart_chunk_selection(search_results, user_question)
        
        # Step 3: Text analysis
        st.write("📝 Step 3 of 7: Analyzing text content...")
        answer_text = ai_complete_on_text(sp_session, user_question, deduped_results)
        
        # Step 4: Extract citations
        st.write("📚 Step 4 of 7: Extracting citations...")
        answer_text_str = answer_text.get("result", "") if isinstance(answer_text, dict) else str(answer_text)
        cited_docs_pages = extract_cited_docs_and_pages(answer_text_str)
        
        # Step 5: Match images
        st.write("🖼️ Step 5 of 7: Matching relevant images...")
        
        def score_image_relevance(item, question):
            """Score image relevance based on multiple factors"""
            score = 0
            question_lower = question.lower()
            content = item.get('ENRICHED_CHUNK', '').lower()
            raw_content = item.get('RAW_CHUNK_TEXT', '').lower()
            
            # Financial keywords boost
            financial_terms = ['trillion', 'billion', 'million', 'percent', '%', 'assets', 'funds', 'investment', 'expense', 'ratio', 'market', 'share']
            for term in financial_terms:
                if term in content or term in raw_content:
                    score += 10
            
            # Question keyword overlap
            question_words = set(question_lower.split())
            content_words = set(content.split())
            overlap = len(question_words.intersection(content_words))
            score += overlap * 5
            
            # Numerical content bonus
            if any(char.isdigit() for char in content):
                score += 20
            
            # Chart/table indicators
            chart_indicators = ['chart', 'table', 'figure', 'graph', 'data']
            for indicator in chart_indicators:
                if indicator in content:
                    score += 15
            
            return score
        
        # Get all available images and score them
        all_images = [result for result in deduped_results if result.get('IMAGE_FILE_NAME')]
        
        if all_images:
            scored_images = [(item, score_image_relevance(item, user_question)) for item in all_images]
            scored_images.sort(key=lambda x: x[1], reverse=True)
            matched_images = [item for item, score in scored_images[:MAX_IMAGES_TO_ANALYZE]]
            st.write(f"Found {len(all_images)} total images, analyzing top {len(matched_images)} most relevant")
        else:
            matched_images = []
            st.write("No images found for analysis")
        
        # Step 6: Process citations and create fallback if needed
        st.write("⚙️ Step 6 of 7: Processing citations...")
        
        if not cited_docs_pages:
            st.write("⚠️ No citations found - activating fallback mode")
            for result in matched_images[:5]:
                doc_name = result.get('ORIGINAL_FILE_NAME', 'Unknown')
                page_num = str(result.get('PAGE_NUMBER', 0))
                if doc_name not in cited_docs_pages:
                    cited_docs_pages[doc_name] = set()
                cited_docs_pages[doc_name].add(page_num)
            st.write(f"✅ Created fallback citations for {len(cited_docs_pages)} documents")
        
        # Step 7: Synthesize
        st.write("🧪 Step 7 of 7: Synthesize final answer")
        st.write("Synthesizing text + image answers into a final response...")
        
        # Process images with progress tracking
        image_critiques = []
        if matched_images:
            progress_placeholder = st.empty()
            
            def process_limited_images():
                """Process images synchronously using Snowpark jobs"""
                critiques = []
                
                for i, result in enumerate(matched_images):
                    progress_placeholder.text(f"Processing image critiques... ({i+1}/{len(matched_images)})")
                    
                    job = ai_complete_on_image_async(sp_session, user_question, result, answer_text)
                    resolved_result = resolve_async_job(job)
                    critique = resolved_result.get("RESULT", "") if resolved_result else ""
                    
                    if critique and critique.strip():
                        critiques.append(critique)
                
                return critiques
            
            image_critiques = process_limited_images()
            progress_placeholder.empty()
        
        # Combine text and image results
        final_answer = answer_text_str
        if image_critiques:
            combined_critique = '\n\n'.join([c for c in image_critiques if c and c.strip()])
            if combined_critique:
                final_answer += f"\n\n**Additional Image Analysis:**\n{combined_critique}"
        
        # Performance metrics
        total_time = time.time() - start_time
        
        # STORE ALL RESULTS IN SESSION STATE
        st.session_state.main_results = {
            'question': user_question,
            'search_results': search_results,
            'deduped_results': deduped_results,
            'matched_images': matched_images,
            'answer_text_str': answer_text_str,
            'cited_docs_pages': cited_docs_pages,
            'image_critiques': image_critiques,
            'final_answer': final_answer,
            'total_time': total_time
        }
        st.session_state.main_question_processed = True

# ========================================
# DISPLAY MAIN RESULTS (INDEPENDENT)
# ========================================

if st.session_state.main_question_processed and 'main_results' in st.session_state:
    results = st.session_state.main_results
    
    # Display final answer
    st.markdown("## 🎯 Final Answer:")
    st.markdown(results['final_answer'])
    
    # Performance metrics
    st.markdown(f"⏱️ **Total time taken:** {results['total_time']:.2f} seconds")

# ========================================
# DEBUG SECTIONS (INDEPENDENT)
# ========================================

if st.session_state.main_question_processed and 'main_results' in st.session_state:
    results = st.session_state.main_results
    
    with st.expander("🔧 Debug - Pipeline Diagnostics"):
        st.write("**🔍 DIAGNOSTIC - Search Results:**")
        st.write(f"Total search results: {len(results['search_results']) if results['search_results'] else 0}")
        st.write(f"After smart selection: {len(results['deduped_results']) if results['deduped_results'] else 0}")
        
        st.write("**🔍 DIAGNOSTIC - Extracted Citations:**")
        st.write(f"Citations found: {dict(results['cited_docs_pages']) if results['cited_docs_pages'] else {}}")
        st.write(f"Number of cited documents: {len(results['cited_docs_pages']) if results['cited_docs_pages'] else 0}")
        
        st.write("**🔍 DIAGNOSTIC - Text Answer Sample:**")
        st.write(f"Answer text (first 500 chars): {results['answer_text_str'][:500]}...")
        
        st.write("**🔍 DIAGNOSTIC - Available Images:**")
        for i, result in enumerate(results['matched_images'][:5]):
            doc_name = result.get('ORIGINAL_FILE_NAME', 'Unknown')
            img_file = result.get('IMAGE_FILE_NAME', 'Unknown')
            st.write(f"Image {i+1}: {doc_name} -> {img_file}")
        
        st.write("**🔍 DIAGNOSTIC - Final Results:**")
        st.write(f"Total jobs created: {len(results['image_critiques'])}")
        st.write(f"Successful critiques: {len([c for c in results['image_critiques'] if c and c.strip()])}")

# ========================================
# IMAGE ANALYSIS SECTION (COMPLETELY INDEPENDENT)
# ========================================

if st.session_state.main_question_processed and 'main_results' in st.session_state:
    results = st.session_state.main_results
    matched_images = results['matched_images']
    
    with st.expander("🔍 Debug - Raw Image Answers"):
        if matched_images:
            st.write(f"Found {len(matched_images)} relevant images for analysis:")
            
            for i, ans in enumerate(matched_images):
                st.markdown(f"### 📄 **Image {i+1}**")
                
                # Display image metadata
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write(f"**📄 Document:** {ans.get('ORIGINAL_FILE_NAME', 'Unknown')}")
                    st.write(f"**🖼️ Image File:** {ans.get('IMAGE_FILE_NAME', 'Unknown')}")
                    st.write(f"**📄 Page:** {ans.get('PAGE_NUMBER', 'Unknown')}")
                
                with col2:
                    content_preview = ans.get('ENRICHED_CHUNK', 'No content available')[:200]
                    st.write(f"**📝 Content Preview:** {content_preview}...")
                
                # Display the actual image
                try:
                    image_file_name = ans.get('IMAGE_FILE_NAME')
                    if image_file_name:
                        image_path = f"@CORTEX_SEARCH_TUTORIAL_DB.PUBLIC.DOC_REPO/{image_file_name}"
                        
                        try:
                            with sp_session.file.get_stream(image_path, decompress=False) as stream:
                                image_bytes = stream.read()
                            st.image(image_bytes, caption=f"Page {ans.get('PAGE_NUMBER', 'Unknown')}", width=300)
                        except Exception as e:
                            st.error(f"Could not load image: {e}")
                            st.write(f"Attempted path: {image_path}")
                            st.write(f"Debug Info:")
                            st.write(f"image_file: {ans.get('IMAGE_FILE_NAME')}")
                            st.write(f"Available ans keys: {list(ans.keys())}")
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                
                # INDEPENDENT CUSTOM QUESTION SECTION
                st.markdown("---")
                st.markdown("**🤔 Ask a custom question about this specific image:**")
                
                # Unique keys for this image
                question_key = f"img_question_{i}"
                result_key = f"img_result_{i}"
                
                # Custom question input with unique key
                custom_question = st.text_input(
                    "Your question:",
                    key=question_key,
                    placeholder="e.g., What are the exact numbers in this chart?",
                    help="Ask specific questions about this image to get targeted analysis"
                )
                
                col_btn1, col_btn2 = st.columns([1, 1])
                
                with col_btn1:
                    # Analysis button - COMPLETELY INDEPENDENT
                    if st.button(f"🔍 Analyze Image", key=f"analyze_btn_{i}"):
                        if custom_question:
                            # Create a unique container for this analysis
                            analysis_container = st.container()
                            with analysis_container:
                                with st.spinner("🧠 Analyzing image with your question..."):
                                    try:
                                        mock_text_answer = {"result": f"Custom question: {custom_question}"}
                                        job = ai_complete_on_image_async(sp_session, custom_question, ans, mock_text_answer)
                                        resolved_result = resolve_async_job(job)
                                        custom_critique = resolved_result.get("RESULT", "") if resolved_result else ""
                                        
                                        # Store result
                                        st.session_state[result_key] = custom_critique
                                        st.success("✅ Analysis complete!")
                                        
                                    except Exception as e:
                                        st.error(f"❌ Error analyzing image: {e}")
                        else:
                            st.warning("⚠️ Please enter a question first.")
                
                # Display stored result INDEPENDENTLY
                if result_key in st.session_state and st.session_state[result_key]:
                    st.success("**🎯 Custom AI Analysis:**")
                    st.markdown(st.session_state[result_key])
                
                with col_btn2:
                    # Clear button - INDEPENDENT
                    if st.button(f"🗑️ Clear", key=f"clear_btn_{i}"):
                        if result_key in st.session_state:
                            del st.session_state[result_key]
                        st.success("🧹 Result cleared!")
                
                st.markdown("---")
        else:
            st.write("No images available for analysis.")
    
    # Hybrid Text Analysis Section
    with st.expander("📊 Debug - Hybrid Text Analysis"):
        if results['deduped_results']:
            st.write("**Enriched vs Raw Content Comparison:**")
            for i, chunk in enumerate(results['deduped_results'][:5]):
                st.markdown(f"### Chunk {i+1}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🤖 Enriched Content:**")
                    enriched = chunk.get('ENRICHED_CHUNK', 'N/A')[:300]
                    st.text_area("", enriched, height=100, key=f"enriched_{i}", disabled=True)
                
                with col2:
                    st.markdown("**📄 Raw Content:**") 
                    raw = chunk.get('RAW_CHUNK_TEXT', 'N/A')[:300]
                    st.text_area("", raw, height=100, key=f"raw_{i}", disabled=True)
                
                st.markdown("---")

st.markdown("---") 