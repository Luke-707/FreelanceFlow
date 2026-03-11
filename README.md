# Freelance Project & Payment Management System

A full-stack web application built with Python and Django for freelancers to manage clients, projects, invoices, and communication.

## Features

*   **User Authentication**: Role-based access (Freelancer/Client).
*   **Project Management**: Track projects, milestones, deadlines, and status.
*   **Payments & Invoices**: Auto-generated invoices on milestone creation, track payments.
*   **Dashboard**: Real-time overview of earnings, pending work, and project stats.
*   **Communication**: Included Chat and Video Call features (using WebRTC/PeerJS).
*   **Design**: Modern glassmorphism UI with Dark Mode.

## Setup Instructions

1.  **Install Python**: Ensure Python is installed on your system.
2.  **Create Virtual Environment** (Optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Apply Migrations**:
    ```bash
    python manage.py makemigrations accounts projects payments communication core
    python manage.py migrate
    ```
5.  **Create Superuser** (Admin):
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run Server**:
    ```bash
    python manage.py runserver
    ```
7.  **Access App**:
    *   Open browser at `http://127.0.0.1:8000/`
    *   Register a new account (Select 'Freelancer' or 'Client').

## Usage Guide

*   **Freelancers**: Create projects, add milestones. Milestones automatically create invoices. Chat with clients.
*   **Clients**: View projects, see invoices. Chat with freelancers.
*   **Video Call**: Navigate to a Client/Freelancer profile or chat to start a video call. (Requires camera/mic permission).

## Project Structure

*   `core/`: Dashboard and main landing logic.
*   `accounts/`: User authentication and model.
*   `projects/`: Project and milestone management.
*   `payments/`: Invoice generation and tracking.
*   `communication/`: Chat and Video Call.
