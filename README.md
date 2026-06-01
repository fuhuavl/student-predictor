## Cara Run

### 1. Run Backend


```bash
uvicorn main:app --reload --port 8000
```

atau

```bash
python -m uvicorn main:app --reload --port 8000
```

---

### 2. Run Frontend

Masuk ke folder frontend:

```bash
cd frontend
```


```bash
streamlit run app.py
```

atau

```bash
python -m streamlit run app.py
```

---

Pastikan backend sudah running sebelum run frontend.
