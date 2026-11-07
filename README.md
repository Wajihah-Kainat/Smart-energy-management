# AI-Powered Smart Energy Management System

## Team Members & Roles
- **Wajihah Kainat** - Subsystem 3: Cost, Savings, Carbon & Score
- **Arshia Fatima** - Subsystem 1: User & Building Management
- **Faryal Mahmood** - Subsystem 4: AI Sustainability Coach & Reports
- **Melika Soheilifar** - Subsystem 2: Energy Monitoring & Dashboard

## Technology Stack
Python, Flask, SQLite, HTML/CSS, Chart.js, OpenAI API, pytest, Docker.

## Subsystem 1: User & Building Management
The UML diagram shows the three classes of Subsystem 1: User, Building and Device, with private attributes and public getters and setters.

One User owns many Buildings (1 to 0..*), and one Building contains many Devices (1 to 0..*); the links are stored as user_id in Building and building_id in Device.

### Uml Diagram
<img width="1380" height="1056" alt="uml_subsystem1" src="https://github.com/user-attachments/assets/ca1374c1-416a-42b7-8570-944d716853d4" />

## Subsystem 2: Energy Monitoring & Dashboard

### Uml Diagram
<img width="1448" height="975" alt="WhatsApp Image 2026-11-07 at 18 39 15" src="https://github.com/user-attachments/assets/f2befd8d-9879-4833-8a40-fa99fb23bccd" />

## Subsystem 3: Cost, Savings, Carbon & Score
### Installation cmd
python -m pip install -r requirements.txt
### Test Cmd
cd subsystem3
python -m pytest -v

### Uml Diagram
<img width="1181" height="732" alt="sub3_uml" src="https://github.com/user-attachments/assets/841658e4-5c35-489a-8207-40ec48fd8545" />

##  Subsystem 4: AI Sustainability Coach & Reports

### Uml Diagram
<img width="1381" height="718" alt="WhatsApp Image 2026-11-07 at 18 29 11" src="https://github.com/user-attachments/assets/cf4395cb-880b-450c-9393-0950ca5dd39d" />

## Presentation Link
