# Step-by-Step Guide: How to Fork, Clone, and Submit Your Assessment

Follow these instructions to participate in the test.

### 1. **Fork the Repository**
1. Go to the repository: [https://github.com/savvpro/savvpro-test-flight](https://github.com/savvpro/savvpro-test-flight)
2. In the top-right corner of the page, click the **Fork** button.
3. This will create a copy of the repository in your GitHub account.

### 2. **Clone Your Fork**
1. After forking, go to your GitHub account and open your **forked repository**.
2. Click on the green **Code** button and copy the URL.
3. Open your terminal and run the following command to clone your fork:
   ```bash
   git clone https://github.com/your-username/savvpro-test-flight.git
   ```
4. Navigate into the cloned directory:
   ```bash
   cd savvpro-test-flight
   ```

### 3. **Read the Task**
1. Open and read [`TASK.md`](https://github.com/savvpro/savvpro-test-flight/blob/main/TASK.md) carefully before writing any code.
2. You are building **FlightHub** — a full-stack flight search and booking system.
3. The required stack is:
   - **Backend:** Python (FastAPI)
   - **Frontend:** Node.js (Express)
4. You **must** use an AI coding agent actively (Claude Code, Cursor, Copilot, etc.) — it is part of the assessment.

### 4. **Create a New Branch**
1. Before making any changes, create a new branch using the following naming pattern:
   ```
   candidate-<your-github-username>
   ```
   Run:
   ```bash
   git checkout -b candidate-<your-github-username>
   ```
   **Example:**
   ```bash
   git checkout -b candidate-johndoe
   ```

### 5. **Complete the Task**
Build the full application on your branch. You must deliver the following:

| File / Folder | Description |
|---|---|
| `README.md` | Setup instructions and assumptions |
| `ARCHITECTURE.md` | Data model, API design, ambiguity decisions |
| `AI_USAGE.md` | AI tool used, key prompts, corrections made |
| `USER_GUIDE.md` | How to use the app — curl examples or screenshots |
| `/backend/` | FastAPI app, runnable with `uvicorn` |
| `/frontend/` | Express app serving an HTML UI |
| `/tests/` | Minimum 3 tests (at least one testing a business rule) |
| `.gitignore` | Appropriate entries |

Make **at least 5 meaningful commits** as you go — not one final dump. Use clear commit messages, for example:
```
feat: add flight search endpoint
feat: implement booking cancellation
fix: handle overbooking edge case
```

### 6. **Push Your Branch**
1. Stage and commit your final changes:
   ```bash
   git add .
   git commit -m "feat: complete FlightHub assessment"
   ```
2. Push your branch to your fork:
   ```bash
   git push origin candidate-<your-github-username>
   ```

---

### **Important Notes**
- **No submissions will be accepted after the deadline.**
