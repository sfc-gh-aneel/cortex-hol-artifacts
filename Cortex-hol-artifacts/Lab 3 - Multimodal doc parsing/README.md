# 🏦 Financial Document AI Assistant

## Overview

A sophisticated multimodal document analysis application built for Snowflake Cortex, specifically designed to analyze the 2023 ICI Investment Company Fact Book with hybrid search capabilities.

## Features

### 🔍 **Hybrid Search Architecture**
- **Multimodal Vector Search**: Combines text and image embeddings using `voyage-multimodal-3`
- **Raw Text Search**: Direct searches on original PDF text for maximum precision
- **Enriched Content Search**: LLM-enhanced text for better context understanding
- **Smart Chunk Selection**: Balances enriched context with raw text precision

### 🤖 **Advanced AI Analysis**
- **Text Analysis**: Uses Claude-4-Sonnet with ICI-specific prompts for financial data precision
- **Image Analysis**: Visual validation against actual document pages with chart/table recognition
- **Interactive Image Questioning**: Ask custom questions about specific charts and images
- **Citation Extraction**: Automatic source linking with presigned URLs

### 🎯 **Performance Optimizations**
- **Smart Image Limiting**: Analyzes only the most relevant images (configurable 1-20)
- **Dynamic Result Limiting**: Adjusts search results based on query complexity
- **Session State Management**: Persistent results without page refreshes
- **Independent Image Analysis**: No interference with main question processing

### 📊 **Debug & Analysis Tools**
- **Pipeline Diagnostics**: Detailed search and selection metrics
- **Hybrid Text Analysis**: Side-by-side comparison of enriched vs raw content
- **Image Debug Section**: Interactive image analysis with custom questioning
- **Performance Metrics**: Timing and processing statistics

## Files

### `streamlit_app.py`
The main Streamlit application with complete multimodal document analysis functionality.

### `MULTIMODAL_DOCUMENT_AI_POC3.ipynb`
Jupyter notebook containing the data processing pipeline and search service setup.

### `2023-factbook.pdf`
The ICI Investment Company Fact Book document used for analysis.

## Technical Architecture

### Data Processing Pipeline
1. **PDF Parsing**: Uses `snowflake.cortex.parse_document` for text extraction
2. **Image Generation**: Converts PDF pages to images for visual analysis
3. **Text Enrichment**: LLM-enhanced chunks with financial context
4. **Vector Embeddings**: Multimodal embeddings for hybrid search
5. **Search Service**: Cortex Search with multiple text and vector indexes

### Search Strategy
- **Multi-Index Query**: Simultaneous search across image vectors, enriched text, raw text, and PDF text
- **Relevance Scoring**: Financial keyword weighting and numerical content prioritization
- **Balanced Selection**: Optimal mix of context-rich and precision-focused chunks

### AI Models
- **Text Analysis**: Claude-4-Sonnet with specialized ICI Fact Book prompts
- **Image Analysis**: Claude-4-Sonnet for visual chart/table interpretation
- **Embeddings**: voyage-multimodal-3 for text-to-image embedding generation

## Usage

1. **Setup**: Ensure Snowflake Cortex environment with required services
2. **Run**: Execute the Streamlit app in Snowflake
3. **Query**: Ask questions about financial data, trends, and asset allocations
4. **Analyze**: Use interactive image features for detailed chart analysis
5. **Debug**: Leverage diagnostic tools for pipeline insights

## Key Capabilities

- **Asset Allocation Analysis**: Comprehensive breakdowns by asset class, fund type, geography
- **Trend Analysis**: Multi-year financial data trends with precise temporal context
- **Visual Data Extraction**: Exact numerical values from charts, tables, and infographics
- **Hybrid Validation**: Cross-validation between text analysis and visual verification
- **Interactive Exploration**: Custom questions about specific document sections

This application demonstrates advanced multimodal AI capabilities for financial document analysis, combining the precision of direct text search with the context of LLM enhancement and the authority of visual validation. 