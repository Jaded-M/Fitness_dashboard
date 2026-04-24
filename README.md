# Personal Health Intelligence Platform

A Python and Streamlit application for tracking training, nutrition, body weight, activity, and daily check-ins in one place.

## Current Product Direction

The app is being rebuilt into a cleaner, more portfolio-ready health dashboard with:

- a streamlined command center
- fast daily logging flows
- SQLite-backed health data
- clearer analytics and trend views
- modular components and services

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- SQLite

## Project Structure

- `Fitness.py`
  Main app entry point and dashboard shell.
- `components/`
  Reusable UI pieces such as the design system, overview widgets, and quick logging dialogs.
- `services/`
  Data shaping and summary logic for the app.
- `pages/`
  Secondary Streamlit pages, currently nutrition and muscle atlas.
- `database.py`
  SQLite schema setup and CRUD helpers.
- `ui/`
  Legacy and page-specific UI modules still used by the nutrition page.
- `core/`
  Older domain logic and migration scripts retained during the rebuild.

## Features

- workout logging
- meal and macro logging
- step tracking
- body-weight tracking
- daily check-ins
- weekly readiness and summary metrics
- nutrition and activity trend charts

## Run Locally

```bash
streamlit run Fitness.py
```

## Status

This project is actively being cleaned up and refactored. The current focus is:

- removing redundant files
- tightening architecture
- improving dark-mode product quality
- rebuilding analytics in phases
