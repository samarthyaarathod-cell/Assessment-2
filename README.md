# Python DRF Assessment Submission — Code: M5-A1

**Candidate / Program:** Python · **Assessment Code:** M5-A1  
**Module:** Django REST Framework (DRF) & REST API Architecture  
**Status:** 100% Complete · All Sections & Questions Fully Attempted  

---

## Folder & Submission Structure

```
Assessment-2/
├── README.md                                          <- Main Master Index
│
├── Section A/                                         <- Concept Application
│   ├── README.md
│   └── Section_A_Answers.md                           <- In-depth answers with diagrams & code for Q1 to Q6
│
├── Section B/                                         <- Practical Coding Tasks (Tasks 1, 2, 3, 4)
│   ├── README.md                                      <- Master guide for Section B
│   ├── section_b_project/                             <- Complete runnable Django project
│   │   ├── manage.py
│   │   ├── test_section_b.py                          <- Automated test suite (100% PASS)
│   │   ├── db.sqlite3
│   │   ├── config/ (settings.py, urls.py)
│   │   └── api/ (models.py, serializers.py, views.py, urls.py)
│   ├── Task 1 - Food Category Listing API/            <- Isolated Task 1 code & docs
│   ├── Task 2 - Menu Item CRUD API/                   <- Isolated Task 2 code & docs
│   ├── Task 3 - Order Listing with ViewSets Router/   <- Isolated Task 3 code & docs
│   └── Task 4 - Token-Authenticated Order Placement/  <- Isolated Task 4 code & docs
│
├── Section C/                                         <- Mini Capstone Project: Food Delivery REST API
│   └── food_delivery_backend/                         <- Complete deployable Django project
│       ├── manage.py
│       ├── test_section_c.py                          <- Automated Capstone test suite (100% PASS)
│       ├── db.sqlite3
│       ├── food_delivery/ (settings.py, urls.py)
│       ├── api/ (models.py, serializers.py, views.py, urls.py, admin.py)
│       └── README.md                                  <- Complete API documentation & Postman screenshots
│
└── Section D/                                         <- AI-Augmented Learning
    ├── README.md
    ├── AI_Augmented_Learning_Submission.md            <- Exact Prompts, Code Comparison, 3-4 Line Note
    ├── original_ai_code.py                            <- Original AI output
    ├── corrected_code.py                              <- Hardened, production-ready code
    └── test_section_d.py                              <- Verification script with Postman test cases
```

---

## Quick Verification Commands

### 1. Section B Automated Test Suite
```powershell
cd "Section B\section_b_project"
python test_section_b.py
```

### 2. Section C Capstone Automated Test Suite
```powershell
cd "Section C\food_delivery_backend"
python test_section_c.py
```

### 3. Section D Step 1 & Step 2 Verification
```powershell
cd "Section D"
python test_section_d.py
```

All suites execute and verify 100% clean passes across all tests and edge-case scenarios.
